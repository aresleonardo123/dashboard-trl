# kpis.py
from streamlit.components.v1 import html

def mostrar_kpis(formularios, trl_max, aprobados, docente_si, docente_no):
    html(f"""
    <style>
    .kpi-container {{
        display: flex;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 20px;
        margin-top: 30px;
    }}
    .kpi-card {{
        flex: 1;
        min-width: 180px;
        padding: 20px;
        background: rgba(40, 40, 40, 0.85);
        border-radius: 16px;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
        text-align: center;
        transition: transform 0.3s ease;
        border: 1px solid rgba(255,255,255,0.08);
    }}
    .kpi-card:hover {{
        transform: translateY(-5px);
    }}
    .kpi-label {{
        font-size: 0.9rem;
        color: #bbb;
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }}
    .kpi-value {{
        font-size: 2.8rem;
        font-weight: bold;
        color: #2ecc71;
        animation: countUp 1.4s ease-out;
    }}
    @keyframes countUp {{
        0% {{ opacity: 0; transform: translateY(10px) scale(0.95); }}
        100% {{ opacity: 1; transform: translateY(0) scale(1); }}
    }}
    </style>

    <div class="kpi-container">
        <div class="kpi-card">
            <div class="kpi-label">Formularios</div>
            <div class="kpi-value">{formularios}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">TRL más alto</div>
            <div class="kpi-value" style="color:#3498db">{trl_max}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Proyectos aprobados</div>
            <div class="kpi-value">{aprobados}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Con docente</div>
            <div class="kpi-value" style="color:#f1c40f">{docente_si}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Sin docente</div>
            <div class="kpi-value" style="color:#e67e22">{docente_no}</div>
        </div>
    </div>
    """, height=300)
