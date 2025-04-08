# main.py
import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
from urllib.parse import quote
import os
from estilos import css_global
from utils import (
    cargar_diccionario,
    obtener_todas_las_entradas,
    calcular_puntajes_por_segmento,
    segmento_trl,
    generar_html_reporte,
    generar_graficos
)

# --- CONFIGURACIÓN Y ESTILOS ---
st.set_page_config(page_title="Dashboard TRL", layout="wide")
st.markdown(css_global, unsafe_allow_html=True)

# --- TÍTULO PRINCIPAL ---
st.title("📊 Dashboard de Evaluación TRL")

# --- AUTENTICACIÓN Y DESCARGA ---
usuario = "multimediafalab"
clave_app = st.text_input("🔐 Contraseña de aplicación WordPress", type="password")
url_formulario = "https://fablab.ucontinental.edu.pe/wp-json/gf/v2/forms/9/entries"
diccionario = cargar_diccionario("diccionario.csv")

# --- ACTUALIZACIÓN DE DATOS ---
df = None
if st.button("🔄 Actualizar datos desde Gravity Forms"):
    if clave_app:
        with st.spinner("Conectando con el servidor..."):
            df = obtener_todas_las_entradas(usuario, clave_app, url_formulario)
            if not df.empty:
                df.to_csv("datos_formularios.csv", index=False)
                st.success(f"✅ Se importaron {len(df)} registros y se guardaron en 'datos_formularios.csv'.")
            else:
                st.warning("⚠️ No se encontraron entradas.")
    else:
        st.warning("Por favor, ingresa tu contraseña de aplicación.")

# --- CARGA LOCAL ---
if df is None and os.path.exists("datos_formularios.csv"):
    df = pd.read_csv("datos_formularios.csv")
    st.info("📁 Cargando datos desde archivo local 'datos_formularios.csv'")

# --- PROCESAMIENTO DE DATOS ---
if df is not None and not df.empty:
    df["Nombre del Proyecto"] = df["1"]
    df["Nivel TRL"] = pd.to_numeric(df["14"], errors="coerce")

    for segmento in ["TRL 1-3", "TRL 4-7", "TRL 8-9"]:
        df[f"Puntaje {segmento}"] = 0.0
    df["Aprobado"] = "No"

    for idx, row in df.iterrows():
        puntajes = calcular_puntajes_por_segmento(row, diccionario)
        for segmento in puntajes:
            df.loc[idx, f"Puntaje {segmento}"] = puntajes[segmento]
        if any(p >= 50 for p in puntajes.values()):
            df.loc[idx, "Aprobado"] = "Sí"

    df["Segmento TRL"] = df["Nivel TRL"].apply(segmento_trl)

    # --- VISTA PREVIA ---
    st.subheader("📄 Vista previa")
    st.dataframe(df[["1", "Aprobado", "Puntaje TRL 1-3", "Puntaje TRL 4-7", "Puntaje TRL 8-9"]].head())

    # --- KPIs ---
    st.subheader("📌 Indicadores clave")

    # Asignación de columnas para docente e inglés
    columna_docente = "15"
    columna_ingles = "17"

    if columna_docente in df.columns:
        df[columna_docente] = df[columna_docente].astype(str)
        df["Docente Acompañante"] = df[columna_docente].str.strip().str.upper() == "SI"
        docentes_presentes = df["Docente Acompañante"].sum()
        docentes_faltantes = len(df) - docentes_presentes
    else:
        docentes_presentes = docentes_faltantes = 0

    if columna_ingles in df.columns:
        df[columna_ingles] = df[columna_ingles].astype(str)
        df["Nivel de Inglés"] = df[columna_ingles].fillna("No especificado").str.strip().str.capitalize()
        proyectos_con_ingles = (df["Nivel de Inglés"] != "Básico") & (df["Nivel de Inglés"] != "No especificado")
        num_proyectos_ingles = proyectos_con_ingles.sum()
    else:
        num_proyectos_ingles = 0

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Formularios", len(df))
    col2.metric("TRL más alto", df["Nivel TRL"].max())
    col3.metric("Proyectos aprobados", (df["Aprobado"] == "Sí").sum())
    col4.metric("Con docente", docentes_presentes)
    col5.metric("Con inglés medio/avanzado", num_proyectos_ingles)

    # --- GRÁFICOS ---
    st.subheader("📈 Visualizaciones")
    fig1, fig2, fig3, fig4 = generar_graficos(df)

    colg1, colg2 = st.columns(2)
    with colg1:
        st.plotly_chart(fig1, use_container_width=True)
    with colg2:
        st.plotly_chart(fig2, use_container_width=True)

    colg3, colg4 = st.columns(2)
    with colg3:
        st.plotly_chart(fig3, use_container_width=True)
    with colg4:
        st.plotly_chart(fig4, use_container_width=True)

    # --- BÚSQUEDA Y REPORTE ---
    nombre_busqueda = st.text_input("🔎 Buscar proyecto para reporte")
    if nombre_busqueda:
        df_filtrado = df[df["Nombre del Proyecto"].str.lower().str.contains(nombre_busqueda.lower(), na=False)]
        if not df_filtrado.empty:
            nombres_unicos = df_filtrado["Nombre del Proyecto"].unique()
            nombre_seleccionado = nombres_unicos[0] if len(nombres_unicos) == 1 else st.radio("Selecciona el proyecto:", options=nombres_unicos)
            df_proyecto = df_filtrado[df_filtrado["Nombre del Proyecto"] == nombre_seleccionado]
            if st.button("📄 Ver reporte con botón de impresión"):
                puntajes = {
                    "TRL 1-3": df_proyecto["Puntaje TRL 1-3"].values[0],
                    "TRL 4-7": df_proyecto["Puntaje TRL 4-7"].values[0],
                    "TRL 8-9": df_proyecto["Puntaje TRL 8-9"].values[0],
                }
                aprobado = df_proyecto["Aprobado"].values[0]
                html = generar_html_reporte(nombre_seleccionado, puntajes, aprobado)
                components.html(html, height=800, scrolling=True)
        else:
            st.warning("⚠️ Proyecto no encontrado. Verifica el nombre.")
