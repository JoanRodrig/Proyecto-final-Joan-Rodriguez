# views.py
from django.shortcuts import render, redirect
import base64
from django.core.files.base import ContentFile
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from .models import ImagenCorporal, EvaluacionFisica
from IA_bodyfat.ia import predecir_con_imagen
from mysite.utils import generar_grafico_progreso


class EvaluacionIAView(LoginRequiredMixin, TemplateView):
    template_name = 'evaluacion_ia.html'

    def post(self, request, *args, **kwargs):
        try:
            altura = float(request.POST.get('altura'))
            peso = float(request.POST.get('peso'))
        except (TypeError, ValueError):
            return JsonResponse({'error': 'Datos de altura o peso inválidos'}, status=400)

        if not request.user.sexo:
            return JsonResponse({'error': 'Debes definir tu sexo en el perfil'}, status=400)

        genero = 0 if request.user.sexo == 'M' else 1

        imagen_obj = None
        path = None

        # Procesar imagen subida desde archivo
        if 'imagen' in request.FILES:
            imagen_file = request.FILES['imagen']
            imagen_obj = ImagenCorporal.objects.create(usuario=request.user, imagen=imagen_file)
            path = imagen_obj.imagen.path

        # Procesar imagen desde cámara (base64)
        elif 'imagen_base64' in request.POST:
            try:
                format, imgstr = request.POST['imagen_base64'].split(';base64,')
                ext = format.split('/')[-1]
                img_data = ContentFile(base64.b64decode(imgstr), name='captura.' + ext)
                imagen_obj = ImagenCorporal.objects.create(usuario=request.user, imagen=img_data)
                path = imagen_obj.imagen.path
            except Exception:
                return JsonResponse({'error': 'No se pudo procesar la imagen de la cámara'}, status=400)

        else:
            return JsonResponse({'error': 'No se proporcionó ninguna imagen'}, status=400)

        # Ejecutar predicción con IA
        try:
            prediccion, clasif = predecir_con_imagen(path, altura, peso, genero, return_results=True)
        except Exception as e:
            return JsonResponse({'error': f'Error en predicción: {str(e)}'}, status=500)

        # Guardar resultado
        EvaluacionFisica.objects.create(
            usuario=request.user,
            imagen=imagen_obj,
            porcentaje_grasa=prediccion,
            postura="Automática",
            comentarios=f"Clasificación: {clasif}"
        )

        return JsonResponse({
            'porcentaje_grasa': round(prediccion, 2),
            'clasificacion': clasif
        })



def index(request):
    return render(request, 'core/index.html',)



class ProgresoView(LoginRequiredMixin, TemplateView):
    template_name = 'progreso.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['grafico'] = generar_grafico_progreso(self.request.user)
        return context


def comunidad(request):
    return render(request, 'core/comunidad.html')

def evaluacion_ia(request):
    return render(request, 'core/evaluacion_ia.html')
