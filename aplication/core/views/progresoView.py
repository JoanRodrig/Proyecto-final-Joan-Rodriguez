from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from aplication.core.models import EvaluacionFisica
from mysite.utils import filtrar_evaluaciones_por_rango_fechas
import json


class ProgresoView(LoginRequiredMixin, TemplateView):
    template_name = 'core/progreso.html'
    default_days_range = 90  # Rango por defecto: 90 días

    def get_queryset(self):
        """Obtiene evaluaciones del usuario ordenadas por fecha"""
        return EvaluacionFisica.objects.filter(
            usuario=self.request.user,
            procesada=True
        ).select_related('usuario').order_by('fecha')

    def get_filtered_evaluations(self):
        """Filtra evaluaciones según parámetro de días"""
        days = self.request.GET.get('dias', str(self.default_days_range))
        try:
            days = int(days)
        except (ValueError, TypeError):
            days = self.default_days_range

        queryset = self.get_queryset()
        if days > 0:  # Si es 0, mostrar todo el historial
            return filtrar_evaluaciones_por_rango_fechas(queryset, days)
        return queryset

    def calcular_metricas(self, evaluaciones):
        """Calcula las métricas de progreso"""
        primera = evaluaciones.first()  # Más antigua
        ultima = evaluaciones.last()    # Más reciente
        
        return {
            'primera_fecha': primera.fecha.strftime('%d/%m/%Y'),
            'total_evaluaciones': evaluaciones.count(),
            'diferencia_peso': ultima.peso_kg - primera.peso_kg if primera.peso_kg is not None and ultima.peso_kg is not None else None,
            'porcentaje_peso': ((ultima.peso_kg - primera.peso_kg) / primera.peso_kg * 100) if primera.peso_kg is not None and ultima.peso_kg is not None and primera.peso_kg != 0 else None,
            'diferencia_grasa': ultima.porcentaje_grasa - primera.porcentaje_grasa if primera.porcentaje_grasa is not None and ultima.porcentaje_grasa is not None else None
        }

    def get_context_data(self, **kwargs):
        """Prepara el contexto para la plantilla"""
        context = super().get_context_data(**kwargs)
        evaluaciones_filtradas = self.get_filtered_evaluations()
        
        context.update({
            'evaluaciones': evaluaciones_filtradas,
            'has_data': evaluaciones_filtradas.exists(),
            'dias_filtro': str(self.request.GET.get('dias', str(self.default_days_range)))
        })

        if context['has_data']:
            # Preparar datos para gráficos - asegurando que no haya None
            fechas = []
            pesos = []
            grasas = []
            
            for e in evaluaciones_filtradas:
                fechas.append(e.fecha.isoformat())
                pesos.append(float(e.peso_kg) if e.peso_kg is not None else None)
                grasas.append(float(e.porcentaje_grasa) if e.porcentaje_grasa is not None else None)
            
            # Filtrar entradas donde ambos valores son None
            datos_filtrados = [
                (f, p, g) for f, p, g in zip(fechas, pesos, grasas)
                if p is not None or g is not None
            ]
            
            if datos_filtrados:
                fechas_filtradas, pesos_filtrados, grasas_filtradas = zip(*datos_filtrados)
                
                # Convertir a JSON correctamente para el template
                import json
                context['grafico_data'] = {
                    'fechas': json.dumps(list(fechas_filtradas)),
                    'pesos': json.dumps([p for p in pesos_filtrados if p is not None]),
                    'grasas': json.dumps([g for g in grasas_filtradas if g is not None]),
                    'fechas_pesos': json.dumps([f for f, p in zip(fechas_filtradas, pesos_filtrados) if p is not None]),
                    'fechas_grasas': json.dumps([f for f, g in zip(fechas_filtradas, grasas_filtradas) if g is not None])
                }
            else:
                context['grafico_data'] = {
                    'fechas': json.dumps([]),
                    'pesos': json.dumps([]),
                    'grasas': json.dumps([]),
                    'fechas_pesos': json.dumps([]),
                    'fechas_grasas': json.dumps([])
                }
            
            # Calcular métricas
            context['metricas'] = self.calcular_metricas(evaluaciones_filtradas)
        
        return context