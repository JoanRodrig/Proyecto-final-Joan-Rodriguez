# utils.py (versión actualizada)
from datetime import timedelta
from django.utils import timezone


def calcular_metricas_progreso(evaluaciones):
    """
    Calcula métricas de progreso basado en evaluaciones físicas
    """
    if not evaluaciones.exists():
        return None

    primera = evaluaciones.earliest("fecha")
    ultima = evaluaciones.latest("fecha")

    metricas = {
        "total_evaluaciones": evaluaciones.count(),
        "primera_fecha": primera.fecha,
        "ultima_fecha": ultima.fecha,
    }

    if primera.peso_kg and ultima.peso_kg:
        diferencia = ultima.peso_kg - primera.peso_kg
        metricas.update(
            {
                "diferencia_peso": round(diferencia, 2),
                "porcentaje_peso": (
                    round((diferencia / primera.peso_kg) * 100, 2)
                    if primera.peso_kg
                    else 0
                ),
            }
        )

    if primera.porcentaje_grasa and ultima.porcentaje_grasa:
        metricas["diferencia_grasa"] = round(
            ultima.porcentaje_grasa - primera.porcentaje_grasa, 2
        )

    return metricas


def filtrar_evaluaciones_por_rango_fechas(evaluaciones, dias=30):
    """
    Filtra evaluaciones dentro de un rango de días

    Args:
        evaluaciones: QuerySet de EvaluacionFisica
        dias (int): Número de días a considerar (por defecto 30)

    Returns:
        QuerySet: Evaluaciones filtradas por el rango de fechas
    """
    try:
        fecha_limite = timezone.now() - timedelta(days=dias)
        return evaluaciones.filter(fecha__gte=fecha_limite)
    except Exception as e:
        logger.error(f"Error filtrando evaluaciones por fecha: {e}")
        return evaluaciones.none()  # Retorna queryset vacío en caso de error
