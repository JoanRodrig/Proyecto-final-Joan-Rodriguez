from django.core.files.base import ContentFile
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from aplication.core.models import EvaluacionFisica, Recomendacion
from IA_bodyfat.ia import predecir_con_imagen
import base64


class EvaluacionIAView(LoginRequiredMixin, TemplateView):
    template_name = "core/evaluacion_ia.html"

    def post(self, request, *args, **kwargs):
        try:
            altura = float(request.POST.get("altura"))
            peso = float(request.POST.get("peso"))
        except (TypeError, ValueError):
            return JsonResponse(
                {"error": "Datos de altura o peso inválidos"}, status=400
            )

        if not request.user.sexo:
            return JsonResponse(
                {"error": "Debes definir tu sexo en el perfil"}, status=400
            )

        genero = 0 if request.user.sexo == "M" else 1
        
        # Procesar imagen
        imagen_file = None
        if "imagen" in request.FILES:
            imagen_file = request.FILES["imagen"]
        elif "imagen_base64" in request.POST:
            try:
                format, imgstr = request.POST["imagen_base64"].split(";base64,")
                ext = format.split("/")[-1]
                imagen_file = ContentFile(
                    base64.b64decode(imgstr), name="captura." + ext
                )
            except Exception:
                return JsonResponse(
                    {"error": "No se pudo procesar la imagen"}, status=400
                )
        else:
            return JsonResponse({"error": "No se proporcionó imagen"}, status=400)

        # Crear evaluación
        evaluacion = EvaluacionFisica.objects.create(
            usuario=request.user, 
            imagen=imagen_file, 
            altura_cm=altura, 
            peso_kg=peso,
            procesada=True  # Añadir esto para marcar como procesada
        )

        try:
            # Obtener predicción
            resultado = predecir_con_imagen(
                evaluacion.imagen.path, altura, peso, genero
            )

            # Buscar recomendación
            recomendacion = Recomendacion.objects.filter(
                porcentaje_min__lte=resultado["prediccion"],
                porcentaje_max__gt=resultado["prediccion"],
                sexo=request.user.sexo,
            ).first()

            if not recomendacion:
                recomendacion = Recomendacion.objects.filter(
                    porcentaje_min__lte=resultado["prediccion"],
                    porcentaje_max__gt=resultado["prediccion"],
                    sexo__isnull=True,
                ).first()

            # Actualizar evaluación
            evaluacion.porcentaje_grasa = resultado["prediccion"]
            if recomendacion:
                evaluacion.recomendacion_msj = recomendacion.mensaje
            evaluacion.procesada = True  # Asegurarse de marcarla como procesada
            evaluacion.save()

            # Actualizar datos del usuario
            evaluacion.actualizar_datos_usuario()

            return JsonResponse(
                {
                    "genero": "Hombre" if request.user.sexo == "M" else "Mujer",
                    "medidas": {
                        "Neck": float(
                            resultado["medidas"]["Neck"]
                        ),  # Convertir a float
                        "Abdomen": float(resultado["medidas"]["Abdomen"]),
                        "Hip": float(resultado["medidas"]["Hip"]),
                    },
                    "altura": float(altura),  # Asegurarse de que sea float
                    "peso": float(peso),
                    "porcentaje_grasa": float(
                        resultado["prediccion"]
                    ),  # Convertir a float
                    "clasificacion": (
                        recomendacion.nombre if recomendacion else "No clasificado"
                    ),
                    "recomendacion": (
                        recomendacion.mensaje
                        if recomendacion
                        else "Consulte con un profesional"
                    ),
                }
            )

        except Exception as e:
            evaluacion.delete()
            return JsonResponse({"error": str(e)}, status=500)
