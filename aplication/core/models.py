from django.db import models
from django.conf import settings
from mysite.const import OBJETIVO_CHOICES
from django.core.validators import MinValueValidator


class ImagenCorporal(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="imagenes_corporales",
    )
    imagen = models.ImageField(upload_to="imagenes_corporales/")
    fecha_subida = models.DateTimeField(auto_now_add=True)
    procesada = models.BooleanField(default=False)

    def __str__(self):
        return f"Imagen de {self.usuario.username} ({self.fecha_subida})"





class EvaluacionFisica(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="evaluaciones"
    )
    imagen = models.ForeignKey(
        ImagenCorporal, on_delete=models.CASCADE, related_name="evaluaciones"
    )
    porcentaje_grasa = models.FloatField(null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    objetivo = models.CharField(
        max_length=50, choices=OBJETIVO_CHOICES, null=True, blank=True
    )

    class Meta:
        ordering = ["-fecha"]





class PlanEntrenamiento(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name="planes_entrenamiento"
    )
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    dias_por_semana = models.IntegerField(validators=[MinValueValidator(1)])
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)


class PlanNutricion(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name="planes_nutricion"
    )
    descripcion = models.TextField()
    calorias = models.IntegerField()
    macros = models.JSONField(null=True, blank=True)  # Proteínas, carbohidratos, grasas
    fecha_asignacion = models.DateTimeField(auto_now_add=True)


class Progreso(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name="progresos"
    )
    fecha = models.DateField(auto_now_add=True)
    peso_actual = models.FloatField()
    grasa_estimada = models.FloatField()
    foto_progreso = models.ForeignKey(
        ImagenCorporal, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    nota = models.TextField(blank=True)


class PostComunidad(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    imagen = models.ImageField(upload_to="comunidad/", null=True, blank=True)


class MensajeMotivacional(models.Model):
    texto = models.CharField(max_length=255)
    categoria = models.CharField(
        max_length=50
    )  # ejemplo: “Progreso”, “Inicio”, “Estancamiento”
