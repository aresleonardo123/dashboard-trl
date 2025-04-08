# main.py
import os
import streamlit as st
import pandas as pd

from config import configurar_pagina
from estilos import aplicar_estilos
from auth import obtener_todas_las_entradas
from funciones import segmento_trl, calcular_puntajes_por_segmento
from data_loader import cargar_diccionario
from kpis import mostrar_kpis
from visualizaciones import graficos_generales, mostrar_en_pares
from reporte import generar_html_reporte
from streamlit.components.v1 import html, components
from streamlit.components.v1 import html


# --- CONFIGURACIÓN Y ESTILOS ---
configurar_pagina()
aplicar_estilos()

st.empty()  # Render previo
st.subheader("📈 Visualizaciones")

# --- CARGA DE DATOS Y AUTENTICACIÓN ---
usuario = "multimediafalab"
clave_app = st.text_input("🔐 Contraseña de aplicación WordPress", type="password")
url_formulario = "https://fablab.ucontinental.edu.pe/wp-json/gf/v2/forms/9/entries"
diccionario = cargar_diccionario("diccionario.csv")

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

if df is None and os.path.exists("datos_formularios.csv"):
    df = pd.read_csv("datos_formularios.csv")
    st.info("📁 Cargando datos desde archivo local 'datos_formularios.csv'")

# --- PROCESAMIENTO ---
if df is not None and not df.empty:
    df["Nombre del Proyecto"] = df["1"]
    df["Nivel TRL"] = pd.to_numeric(df["14"], errors="coerce")
    df["Puntaje TRL 1-3"] = 0.0
    df["Puntaje TRL 4-7"] = 0.0
    df["Puntaje TRL 8-9"] = 0.0
    df["Aprobado"] = "No"

    for idx, row in df.iterrows():
        puntajes = calcular_puntajes_por_segmento(row, diccionario)
        for segmento in puntajes:
            df.loc[idx, f"Puntaje {segmento}"] = puntajes[segmento]
        if any(p >= 50 for p in puntajes.values()):
            df.loc[idx, "Aprobado"] = "Sí"

    df["Segmento TRL"] = df["Nivel TRL"].apply(segmento_trl)

    # Columnas de interés
    columna_docente = "15"
    columna_industria = "3"
    columna_ingles = "17"
    columna_ubicacion = "30"

    if columna_docente in df.columns:
        df[columna_docente] = df[columna_docente].astype(str)
        df["Docente Acompañante"] = df[columna_docente].str.strip().str.upper() == "SI"

    formularios = len(df)
    trl_max = int(df["Nivel TRL"].max())
    aprobados = int((df["Aprobado"] == "Sí").sum())
    docente_si = int(df["Docente Acompañante"].sum())
    docente_no = formularios - docente_si

    mostrar_kpis(formularios, trl_max, aprobados, docente_si, docente_no)

    # Vista previa
    st.subheader("📄 Vista previa")
    st.dataframe(df[["1", "Aprobado", "Puntaje TRL 1-3", "Puntaje TRL 4-7", "Puntaje TRL 8-9"]].head())

    # Gráficos
    st.subheader("📊 Gráficos")
    figs = graficos_generales(df, columna_industria, columna_ingles, columna_ubicacion)
    mostrar_en_pares(*figs)

    # --- BUSCADOR DE PROYECTOS ---
    with st.form(key="buscar_proyecto_form"):
        nombre_input = st.text_input("🔍 Escribe el nombre exacto del proyecto que deseas exportar",
                                     value=st.session_state.get("nombre_busqueda", ""))
        buscar = st.form_submit_button("🔎 Buscar proyecto")
        if buscar:
            st.session_state["nombre_busqueda"] = nombre_input
            df_filtrado = df[df["Nombre del Proyecto"].str.lower().str.contains(nombre_input.lower(), na=False)]
            st.session_state["df_filtrado"] = df_filtrado
            st.session_state["proyecto_nombres"] = df_filtrado["Nombre del Proyecto"].unique().tolist() if not df_filtrado.empty else []

    if "df_filtrado" in st.session_state and st.session_state["df_filtrado"] is not None:
        df_filtrado = st.session_state["df_filtrado"]
        nombre_input = st.session_state["nombre_busqueda"]

        if not df_filtrado.empty:
            st.success(f"✅ Se encontraron {len(df_filtrado)} proyecto(s) que coinciden con: **{nombre_input}**")


            nombres_unicos = st.session_state.get("proyecto_nombres", [])
            nombre_seleccionado = nombres_unicos[0] if len(nombres_unicos) == 1 else st.radio(
                "Selecciona el proyecto que deseas visualizar:",
                options=nombres_unicos,
                key="radio_proyecto"
            )

            df_proyecto = df_filtrado[df_filtrado["Nombre del Proyecto"] == nombre_seleccionado]

            if st.button("📄 Ver reporte con botón de impresión"):
                puntajes = {
                    "TRL 1-3": df_proyecto["Puntaje TRL 1-3"].values[0],
                    "TRL 4-7": df_proyecto["Puntaje TRL 4-7"].values[0],
                    "TRL 8-9": df_proyecto["Puntaje TRL 8-9"].values[0],
                }
                aprobado = df_proyecto["Aprobado"].values[0]
                html_out = generar_html_reporte(nombre_seleccionado, puntajes, aprobado)
                html(html_out, height=800, scrolling=True)

        else:
            st.warning("⚠️ Proyecto no encontrado. Verifica el nombre.")
