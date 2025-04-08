import plotly.express as px
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go

def crear_layout(titulo):
    return dict(
        title={
            'text': f"<b>{titulo}</b>",
            'font': {'family': "Arial", 'size': 22, 'color': "#2c3e50"},
            'x': 0.5,
            'y': 0.95
        },
        font=dict(family="Arial", size=14, color="#34495e"),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#f8f9fa",
        margin=dict(l=50, r=50, t=80, b=70),
        hoverlabel=dict(
            bgcolor="white",
            font_size=14,
            font_family="Arial",
            bordercolor="#bdc3c7"
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.25,
            xanchor="center",
            x=0.5
        )
    )

def graficos_generales(df, columna_industria, columna_ingles, columna_ubicacion):
    colors = {
        "Sí": "#27ae60",
        "No": "#e74c3c",
        "TRL 1-3": "#3498db",
        "TRL 4-7": "#9b59b6",
        "TRL 8-9": "#e67e22",
        "Ubicación": ["#3498db", "#2ecc71", "#e74c3c", "#f1c40f", "#95a5a6"]
    }

    # Gráfico 1
    registros = []
    for _, row in df[df["Aprobado"] == "Sí"].iterrows():
        for segmento in ["TRL 1-3", "TRL 4-7", "TRL 8-9"]:
            if row[f"Puntaje {segmento}"] >= 50:
                registros.append({"Segmento TRL": segmento})
    df_aprobados = pd.DataFrame(registros)
    conteo_aprobados = df_aprobados["Segmento TRL"].value_counts().reset_index()
    conteo_aprobados.columns = ["Segmento TRL", "Aprobados"]

    fig1 = px.bar(
        conteo_aprobados,
        x="Segmento TRL",
        y="Aprobados",
        color="Segmento TRL",
        color_discrete_map={
            "TRL 1-3": colors["TRL 1-3"],
            "TRL 4-7": colors["TRL 4-7"],
            "TRL 8-9": colors["TRL 8-9"]
        },
        template="plotly_white"
    )
    fig1.update_traces(texttemplate="%{y}", textposition="outside", textfont_size=14)
    fig1.update_layout(**crear_layout("📊 Aprobados por Nivel TRL"), xaxis_title="Segmento TRL", yaxis_title="Número de Proyectos", showlegend=False, height=600)
    fig1.update_xaxes(tickangle=-30)

    # Gráfico 2
    fig2 = px.pie(df, names="Aprobado", hole=0.4, color="Aprobado", color_discrete_map={"Sí": colors["Sí"], "No": colors["No"]}, template="plotly_white")
    fig2.update_traces(textinfo="percent+label", pull=[0.05, 0], textfont_size=14)
    fig2.update_layout(**crear_layout("✅ Proyectos Aprobados"), showlegend=False, height=600)

    # Gráfico 3
    registros = []
    for _, row in df.iterrows():
        for segmento in ["TRL 1-3", "TRL 4-7", "TRL 8-9"]:
            aprobado = "Sí" if row[f"Puntaje {segmento}"] >= 50 else "No"
            registros.append({
                "Segmento TRL": segmento,
                "Aprobado": aprobado
            })
    df_segmentos = pd.DataFrame(registros)
    fig3 = px.histogram(df_segmentos, x="Segmento TRL", color="Aprobado", barmode="group", color_discrete_map={"Sí": colors["Sí"], "No": colors["No"]}, template="plotly_white")
    fig3.update_traces()
    fig3.update_layout(**crear_layout("📈 Aprobación por Segmento TRL"), xaxis_title="Segmento TRL", yaxis_title="Número de Proyectos", height=600)
    fig3.update_xaxes(tickangle=-30)

    # Gráfico 4
    fig4 = px.histogram(df, x="Puntaje TRL 1-3", nbins=20, color_discrete_sequence=[colors["TRL 1-3"]], template="plotly_white")
    fig4.update_layout(**crear_layout("🔍 Puntajes TRL 1-3"), xaxis_title="Puntaje", yaxis_title="Número de Proyectos", height=600)
    fig4.update_xaxes(tickangle=-30)

    # Gráfico 5
    if columna_industria in df.columns:
        df["Industria"] = df[columna_industria].fillna("No especificada").astype(str).str.strip()
        conteo_industria = df["Industria"].value_counts().reset_index()
        conteo_industria.columns = ["Industria", "Cantidad"]
        fig5 = px.bar(conteo_industria, x="Cantidad", y="Industria", orientation="h", color="Industria", template="plotly_white")
        fig5.update_layout(**crear_layout("🏭 Proyectos por Industria"), height=600, showlegend=False)
    else:
        fig5 = None

    # Gráfico 6
    if columna_ingles in df.columns:
        df["Nivel de Inglés"] = df[columna_ingles].fillna("No especificado").str.strip().str.capitalize()
        conteo_ingles = df["Nivel de Inglés"].value_counts().reset_index()
        conteo_ingles.columns = ["Nivel", "Cantidad"]
        fig6 = px.bar(conteo_ingles, x="Nivel", y="Cantidad", color="Nivel", template="plotly_white")
        fig6.update_layout(**crear_layout("🌍 Nivel de Inglés"), height=600, showlegend=False)
        fig6.update_xaxes(tickangle=-30)
    else:
        fig6 = None

    # Gráfico 7
    if columna_ubicacion in df.columns:
        df["Ubicación"] = df[columna_ubicacion].astype(str).str.strip().str.capitalize().replace({"Nan": "No especificada", "": "No especificada"})
        conteo_ubicacion = df["Ubicación"].value_counts().reset_index()
        conteo_ubicacion.columns = ["Ubicación", "Cantidad"]
        fig7 = px.pie(conteo_ubicacion, names="Ubicación", values="Cantidad", hole=0.3, color_discrete_sequence=colors["Ubicación"], template="plotly_white")
        fig7.update_traces(textinfo="percent+label", textfont_size=14)
        fig7.update_layout(**crear_layout("📍 Ubicación Geográfica"), height=600, showlegend=False)
    else:
        fig7 = None

    return fig1, fig2, fig3, fig4, fig5, fig6, fig7
