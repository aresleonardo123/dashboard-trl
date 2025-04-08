from datetime import datetime
from fastapi import FastAPI, HTTPException, Request, Header, Query
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

import pandas as pd
import base64
import numpy as np
from auth import obtener_todas_las_entradas
from funciones import segmento_trl, calcular_puntajes_por_segmento, generar_insights, generar_excel_aprobados
from data_loader import cargar_diccionario
from visualizaciones import graficos_generales
from urllib.parse import unquote
import os
import io
import re
from dotenv import load_dotenv

# Cargar .env
load_dotenv()
APP_PASSWORD = os.getenv("APP_PASSWORD", "").strip()

app = FastAPI()

current_dir = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(current_dir, "templates")
static_dir = os.path.join(templates_dir, "static")

app.mount("/public", StaticFiles(directory="front/public"), name="public")
app.mount("/static", StaticFiles(directory=static_dir), name="static")
app.mount("/assets", StaticFiles(directory="templates/static"), name="assets")

@app.get("/", response_class=FileResponse)
async def serve_spa():
    return FileResponse("templates/static/index.html")

templates = Jinja2Templates(directory=templates_dir)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Validación de autorización básica
def validar_contraseña(authorization: str = Header(...)):
    try:
        tipo, datos = authorization.split(" ")
        decoded = base64.b64decode(datos).decode("utf-8")
        _, password = decoded.split(":", 1)

        password_limpia = password.strip().replace("\u00A0", " ").replace("\u200B", "").replace("\uFEFF", "")
        esperado = APP_PASSWORD.replace("\u00A0", " ").replace("\u200B", "").replace("\uFEFF", "")

        # Validación flexible
        if password != APP_PASSWORD and password_limpia != esperado:
            raise HTTPException(status_code=401, detail="Contraseña incorrecta")

    except Exception as e:
        raise HTTPException(status_code=401, detail="Error en autenticación")

class ProjectRequest(BaseModel):
    nombre: str

def obtener_y_guardar_datos():
    df = obtener_todas_las_entradas(
        usuario="multimediafalab",
        clave_app=APP_PASSWORD,
        url_base="https://fablab.ucontinental.edu.pe/wp-json/gf/v2/forms/9/entries"
    )
    if not df.empty:
        df.to_csv("datos_formularios.csv", index=False)
    return df


def cargar_y_procesar_datos():
    if not os.path.exists("datos_formularios.csv"):
        df = obtener_y_guardar_datos()
    else:
        df = pd.read_csv("datos_formularios.csv")

    diccionario = cargar_diccionario("diccionario.csv")
    return procesar_datos_completos(df, diccionario)

def procesar_datos_completos(df, diccionario):
    df = df.rename(columns={
        "1": "Nombre del Proyecto",
        "14": "Nivel TRL",
        "15": "Docente Acompañante",
        "17": "Nivel de Inglés",
        "30": "Ubicación",
        "3": "Industria"
    })

    df["Nivel TRL"] = pd.to_numeric(df["Nivel TRL"], errors="coerce").fillna(0)
    df["Segmento TRL"] = df["Nivel TRL"].apply(segmento_trl)

    for segmento in ["TRL 1-3", "TRL 4-7", "TRL 8-9"]:
        df[f"Puntaje {segmento}"] = 0.0
    df["Aprobado"] = "No"

    for idx, row in df.iterrows():
        puntajes = calcular_puntajes_por_segmento(row, diccionario)
        extra = 0

        nivel_ingles = str(row.get("Nivel de Inglés", "")).strip().lower()
        if "intermedio" in nivel_ingles:
            extra += 2
        elif "avanzado" in nivel_ingles:
            extra += 4

        docente = str(row.get("Docente Acompañante", "")).strip().lower()
        if docente == "si":
            extra += 10

        for segmento in puntajes:
            df.at[idx, f"Puntaje {segmento}"] = puntajes[segmento] + extra

        if any((puntajes[seg] + extra) >= 50 for seg in puntajes):
            df.at[idx, "Aprobado"] = "Sí"

    df["Docente Acompañante"] = df["Docente Acompañante"].astype(str).str.strip().str.upper() == "SI"
    df["Nivel de Inglés"] = df["Nivel de Inglés"].fillna("No especificado").str.strip().str.capitalize()
    df["Puntaje Total"] = df["Puntaje TRL 1-3"] + df["Puntaje TRL 4-7"] + df["Puntaje TRL 8-9"]
    df["Insights"] = df.apply(lambda row: generar_insights(row, diccionario), axis=1)

    return df

@app.post("/actualizar-datos")
async def actualizar_datos(authorization: str = Header(...)):
    validar_contraseña(authorization)
    try:
        df = obtener_y_guardar_datos()
        return {"mensaje": f"Datos cargados ({len(df)} registros)"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metricas-principales")
async def obtener_metricas(authorization: str = Header(...)):
    validar_contraseña(authorization)
    df = cargar_y_procesar_datos()

    # Top proyecto por segmento TRL
    top_proyectos_trl = {}
    for segmento in ["TRL 1-3", "TRL 4-7", "TRL 8-9"]:
        filtro = df[df["Segmento TRL"] == segmento]
        if not filtro.empty:
            top_row = filtro.loc[filtro["Puntaje Total"].idxmax()]
            top_proyectos_trl[segmento] = top_row["Nombre del Proyecto"]

    # Nivel de inglés más común
    nivel_ingles_mas_comun = df["Nivel de Inglés"].mode().iloc[0] if not df["Nivel de Inglés"].empty else "No especificado"

    return {
        "formularios": len(df),
        "trl_max": int(df["Nivel TRL"].max()),
        "aprobados": int((df["Aprobado"] == "Sí").sum()),
        "docente_si": int(df["Docente Acompañante"].sum()),
        "docente_no": len(df) - int(df["Docente Acompañante"].sum()),
        "puntaje_maximo": round(df["Puntaje Total"].max(), 1),
        "top_proyectos_trl": top_proyectos_trl,
        "nivel_ingles_mas_comun": nivel_ingles_mas_comun
    }

@app.get("/datos-graficos")
async def obtener_datos_graficos(authorization: str = Header(...)):
    validar_contraseña(authorization)
    df = cargar_y_procesar_datos()
    fig1, fig2, fig3, fig4, fig5, fig6, fig7 = graficos_generales(
        df, "Industria", "Nivel de Inglés", "Ubicación"
    )

    return {
        "graficos": {
            "grafico_1": fig1.to_json(),
            "grafico_2": fig2.to_json(),
            "grafico_3": fig3.to_json(),
            "grafico_4": fig4.to_json(),
            "grafico_5": fig5.to_json() if fig5 else None,
            "grafico_6": fig6.to_json() if fig6 else None,
            "grafico_7": fig7.to_json() if fig7 else None,
        }
    }

@app.post("/buscar-proyecto")
async def buscar_proyecto(request: ProjectRequest, authorization: str = Header(...)):   
    validar_contraseña(authorization)
    df = cargar_y_procesar_datos()

    if "Nombre del Proyecto" not in df.columns:
        raise HTTPException(status_code=400, detail="Columna 'Nombre del Proyecto' no encontrada")

    df = df.fillna("")
    resultados = df[df["Nombre del Proyecto"].str.contains(request.nombre, case=False, na=False)]

    if resultados.empty:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    return {"proyectos": resultados.replace({np.nan: None}).to_dict(orient="records")}

@app.get("/proyectos")
async def obtener_proyectos(authorization: str = Header(...)):
    validar_contraseña(authorization)
    df = cargar_y_procesar_datos()
    return {
        "proyectos": df[[
            "Nombre del Proyecto", "Aprobado", "Puntaje TRL 1-3",
            "Puntaje TRL 4-7", "Puntaje TRL 8-9", "Puntaje Total",
            "Segmento TRL", "Industria", "Insights"
        ]].to_dict(orient="records")
    }


@app.get("/reporte-proyecto/{nombre}", response_class=HTMLResponse)
async def generar_reporte_proyecto(
    request: Request,
    nombre: str,
    auth: str = Query(...)
):
    try:
        decoded = base64.b64decode(auth).decode("utf-8")
        _, password = decoded.split(":", 1)

        # Usar la misma lógica de limpieza que en los otros reportes
        password_limpia = password.strip().replace("\u00A0", " ").replace("\u200B", "")
        esperado = APP_PASSWORD.replace("\u00A0", " ").replace("\u200B", "")

        if password_limpia != esperado:
            raise HTTPException(status_code=401, detail="Credenciales inválidas")

    except Exception as e:
        raise HTTPException(status_code=401, detail="Error en autenticación")

    df = cargar_y_procesar_datos()
    nombre_decodificado = unquote(nombre)

    proyecto = df[df["Nombre del Proyecto"].str.contains(re.escape(nombre_decodificado), case=False, na=False)]
    if proyecto.empty:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    proyecto = proyecto.iloc[0]
    insights = generar_insights(proyecto)

    context = {
        "request": request,
        "fecha_generacion": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "nombre_proyecto": proyecto["Nombre del Proyecto"],
        "aprobado": proyecto["Aprobado"],
        "nivel_trl": proyecto["Nivel TRL"],
        "segmento_trl": proyecto["Segmento TRL"],
        "docente_acompanante": "Sí" if proyecto["Docente Acompañante"] else "No",
        "ubicacion": proyecto.get("Ubicación", "No especificada"),
        "nivel_ingles": proyecto.get("Nivel de Inglés", "No especificado"),
        "trl_1_3": proyecto["Puntaje TRL 1-3"],
        "trl_4_7": proyecto["Puntaje TRL 4-7"],
        "trl_8_9": proyecto["Puntaje TRL 8-9"],
        "insights": insights
    }
    return templates.TemplateResponse("reports/reporte_template.html", context)

@app.get("/insights-generales")
async def obtener_insights_generales(authorization: str = Header(...)):
    validar_contraseña(authorization)
    try:
        df = cargar_y_procesar_datos()
        df["Puntaje Total"] = df["Puntaje TRL 1-3"] + df["Puntaje TRL 4-7"] + df["Puntaje TRL 8-9"]

        total = len(df)
        aprobados = int((df["Aprobado"] == "Sí").sum())
        porcentaje = round((aprobados / total) * 100, 1) if total > 0 else 0.0

        distribucion = df["Segmento TRL"].value_counts().to_dict()
        distribucion = {str(k): int(v) for k, v in distribucion.items()}

        promedios = {
            "TRL 1-3": round(df["Puntaje TRL 1-3"].mean(), 1),
            "TRL 4-7": round(df["Puntaje TRL 4-7"].mean(), 1),
            "TRL 8-9": round(df["Puntaje TRL 8-9"].mean(), 1),
            "Total": round(df["Puntaje Total"].mean(), 1)
        }

        top_rows = df.nlargest(3, "Puntaje Total")[["Nombre del Proyecto", "Puntaje Total"]]
        top_proyectos = [
            {"Nombre del Proyecto": str(row["Nombre del Proyecto"]), "Puntaje Total": round(float(row["Puntaje Total"]), 1)}
            for _, row in top_rows.iterrows()
        ]

        insights = [
            f"📊 {aprobados} de {total} proyectos están aprobados ({porcentaje}%)",
            f"🏆 Proyecto con mayor puntaje: {top_proyectos[0]['Nombre del Proyecto']} ({top_proyectos[0]['Puntaje Total']} pts)" if top_proyectos else "No hay proyectos destacados",
            f"🔍 Distribución TRL: {distribucion.get('TRL 1-3', 0)} inicial, {distribucion.get('TRL 4-7', 0)} en desarrollo, {distribucion.get('TRL 8-9', 0)} listos",
            f"📈 Promedios: TRL 1-3: {promedios['TRL 1-3']}, TRL 4-7: {promedios['TRL 4-7']}, TRL 8-9: {promedios['TRL 8-9']}",
            "💡 Recomendación: " + ("Mentoría a proyectos iniciales" if distribucion.get('TRL 1-3', 0) > distribucion.get('TRL 8-9', 0) else "Preparar implementación")
        ]

        return jsonable_encoder({
            "metricas": {
                "total_proyectos": total,
                "aprobados": aprobados,
                "porcentaje_aprobados": porcentaje,
                "distribucion_trl": distribucion,
                "promedios": promedios
            },
            "top_proyectos": top_proyectos,
            "insights": insights
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar insights: {str(e)}")

@app.get("/reporte-aprobados", response_class=StreamingResponse)
async def generar_reporte_aprobados():
    df = cargar_y_procesar_datos()
    aprobados = df[df["Aprobado"] == "Sí"]

    if aprobados.empty:
        raise HTTPException(status_code=404, detail="No hay proyectos aprobados.")

    excel_file = generar_excel_aprobados(aprobados)

    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=proyectos_aprobados.xlsx"
        }
    )
    
@app.get("/reporte-top10", response_class=HTMLResponse)
async def generar_reporte_top10(request: Request, auth: str = Query(...)):
    try:
        decoded = base64.b64decode(auth).decode("utf-8")
        _, password = decoded.split(":", 1)

        password_limpia = password.strip().replace("\u00A0", " ").replace("\u200B", "")
        esperado = APP_PASSWORD.replace("\u00A0", " ").replace("\u200B", "")

        if password_limpia != esperado:
            raise HTTPException(status_code=401, detail="Credenciales inválidas")
    except:
        raise HTTPException(status_code=401, detail="Error en autenticación")

    df = cargar_y_procesar_datos()
    top10 = df.sort_values(by="Puntaje Total", ascending=False).head(10)

    proyectos_contexto = []
    for _, proyecto in top10.iterrows():
        proyectos_contexto.append({
            "nombre_proyecto": proyecto["Nombre del Proyecto"],
            "aprobado": proyecto["Aprobado"],
            "nivel_trl": proyecto["Nivel TRL"],
            "segmento_trl": proyecto["Segmento TRL"],
            "docente_acompanante": "Sí" if proyecto["Docente Acompañante"] else "No",
            "ubicacion": proyecto.get("Ubicación", "No especificada"),
            "nivel_ingles": proyecto.get("Nivel de Inglés", "No especificado"),
            "trl_1_3": proyecto["Puntaje TRL 1-3"],
            "trl_4_7": proyecto["Puntaje TRL 4-7"],
            "trl_8_9": proyecto["Puntaje TRL 8-9"],
            "puntaje_total": proyecto["Puntaje Total"],
            "insights": generar_insights(proyecto),
        })

    return templates.TemplateResponse("reports/reporte_top10.html", {
        "request": request,
        "fecha_generacion": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "proyectos": proyectos_contexto
    })
