# reporte.py
from string import Template

def generar_html_reporte(nombre, puntajes, aprobado, plantilla_path="assets/reporte_template.html"):
    estado_texto = "APROBADO ✅" if aprobado == "Sí" else "NO APROBADO ❌"
    estado_clase = "aprobado" if aprobado == "Sí" else "rechazado"

    with open(plantilla_path, "r", encoding="utf-8") as f:
        html_template = Template(f.read())

    html_render = html_template.safe_substitute({
        "nombre": nombre,
        "estado_texto": estado_texto,
        "estado_clase": estado_clase,
        "trl13": puntajes["TRL 1-3"],
        "trl47": puntajes["TRL 4-7"],
        "trl89": puntajes["TRL 8-9"]
    })
    return html_render
