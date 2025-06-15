# utils.py
import matplotlib.pyplot as plt
import io
import base64
from aplication.core.models import EvaluacionFisica

def generar_grafico_progreso(usuario):
    evaluaciones = EvaluacionFisica.objects.filter(usuario=usuario).order_by('fecha')
    fechas = [e.fecha.strftime('%d/%m') for e in evaluaciones]
    grasas = [e.porcentaje_grasa for e in evaluaciones]

    plt.figure(figsize=(6, 3))
    plt.plot(fechas, grasas, marker='o', color='green')
    plt.title("Progreso de grasa corporal")
    plt.xlabel("Fecha")
    plt.ylabel("Grasa (%)")
    plt.grid(True)
    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    imagen_base64 = base64.b64encode(buffer.getvalue()).decode()
    buffer.close()
    plt.close()

    return f"data:image/png;base64,{imagen_base64}"
