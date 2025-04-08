# data_loader.py
import pandas as pd
import streamlit as st

@st.cache_data
def cargar_diccionario(path="diccionario.csv"):
    df_dic = pd.read_csv(path)
    mapa = {}
    for _, row in df_dic.iterrows():
        pregunta = str(row["Pregunta"]).strip()
        respuesta = str(row["Respuesta"]).strip()
        puntaje = row["Puntaje"]
        segmento = row["Segmento TRL"]
        if pregunta not in mapa:
            mapa[pregunta] = {}
        mapa[pregunta][respuesta] = {"puntaje": puntaje, "segmento": segmento}
    return mapa
