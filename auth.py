# auth.py
import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
import streamlit as st

def obtener_todas_las_entradas(usuario, clave_app, url_base):
    print(f"Credenciales recibidas - Usuario: {usuario}, Clave: {clave_app}")
    all_entries = []
    page = 1
    while True:
        params = {"paging[page_size]": 100, "paging[current_page]": page}
        response = requests.get(url_base, auth=HTTPBasicAuth(usuario, clave_app), params=params)
        if response.status_code != 200:
            st.error(f"Error {response.status_code}: {response.text}")
            return pd.DataFrame()
        data = response.json()
        entries = data.get("entries", [])
        if not entries:
            break
        all_entries.extend(entries)
        if len(entries) < 100:
            break
        page += 1
    return pd.DataFrame(all_entries)
