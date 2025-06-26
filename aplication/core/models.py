from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from mysite.const import OBJETIVO_CHOICES,SEX_CHOICES
from .utils import validate_image_size



class Recomendacion(models.Model):
    """
    Mensaje de recomendación asociado a un rango de porcentaje de grasa,
    al sexo y, opcionalmente, a un objetivo específico.
    """

    nombre = models.CharField(
        max_length=100,
        help_text="Título corto de la recomendación (p.ej. 'Obesidad alta')",
    )

    # Nuevo campo: sexo al que aplica ('M', 'F') o nulo = ambos
    sexo = models.CharField(
        max_length=1,
        choices=SEX_CHOICES,
        null=True, blank=True,
        help_text="Dejar vacío si aplica a ambos sexos"
    )

    objetivo = models.CharField(
        max_length=50,
        choices=OBJETIVO_CHOICES,
        null=True, blank=True,
        help_text="Si aplica solo a un objetivo concreto",
    )

    porcentaje_min = models.FloatField(
        help_text="Valor mínimo de % grasa (inclusive)"
    )
    porcentaje_max = models.FloatField(
        help_text="Valor máximo de % grasa (exclusive)"
    )

    mensaje = models.TextField(
        help_text="Texto que se mostrará al usuario"
    )

    class Meta:
        ordering = ["porcentaje_min"]
        verbose_name = "Recomendación"
        verbose_name_plural = "Recomendaciones"

    def __str__(self):
        rango = f"{self.porcentaje_min}–{self.porcentaje_max}%"
        sexo_txt = dict(SEX_CHOICES).get(self.sexo, "Todos")
        return f"{self.nombre} ({sexo_txt}, {rango})"
    
    
    

class EvaluacionFisica(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="evaluaciones"
    )

    # Imagen directamente en el modelo
    imagen = models.ImageField(
        upload_to="evaluaciones_fisicas/",
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp']),
            validate_image_size
        ],
        help_text="Imagen corporal para la evaluación"
    )
    
    altura_cm = models.FloatField(
        null=True, 
        blank=True, 
        validators=[MinValueValidator(50), MaxValueValidator(250)],
        help_text="Altura en cm"
    )   

    peso_kg = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(30), MaxValueValidator(300)],
        help_text="Peso en kg"
    )

    porcentaje_grasa = models.FloatField(
        null=True, 
        blank=True, 
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    fecha = models.DateTimeField(auto_now_add=True)
    
    procesada = models.BooleanField(default=False)

    objetivo = models.CharField(
        max_length=50, 
        choices=OBJETIVO_CHOICES, 
        null=True, 
        blank=True
    )

    recomendacion_msj = models.TextField(
        null=True,
        blank=True,
        help_text="Mensaje de recomendación basado en % de grasa y sexo",
    )
    
    class Meta:
        ordering = ['-fecha']
        verbose_name = "Evaluación Física"
        verbose_name_plural = "Evaluaciones Físicas"
    
    def save(self, *args, **kwargs):
        # Tu lógica existente para recomendaciones
        if self.porcentaje_grasa is not None and self.usuario.sexo:
            recomendacion_obj = self._buscar_recomendacion()
            
            if recomendacion_obj:
                if recomendacion_obj.objetivo:
                    self.objetivo = recomendacion_obj.objetivo
                self.recomendacion = recomendacion_obj.mensaje
        
        super().save(*args, **kwargs)

    def _buscar_recomendacion(self):
        """Tu método existente sin cambios"""
        filtros_base = {
            "porcentaje_min__lte": self.porcentaje_grasa,
            "porcentaje_max__gt": self.porcentaje_grasa,
        }
        
        filtros_sexo = filtros_base.copy()
        filtros_sexo["sexo"] = self.usuario.sexo
        
        recomendacion = Recomendacion.objects.filter(**filtros_sexo).first()
        
        if not recomendacion:
            filtros_general = filtros_base.copy()
            filtros_general["sexo__isnull"] = True
            recomendacion = Recomendacion.objects.filter(**filtros_general).first()
        
        return recomendacion
            
    def actualizar_datos_usuario(self):
        """Tu método existente sin cambios"""
        if self.peso_kg:
            self.usuario.peso_kg = self.peso_kg
        if self.altura_cm:
            self.usuario.altura_cm = self.altura_cm
        
        campos_actualizar = []
        if self.peso_kg:
            campos_actualizar.append('peso_kg')
        if self.altura_cm:
            campos_actualizar.append('altura_cm')
        
        if campos_actualizar:
            self.usuario.save(update_fields=campos_actualizar)

    def __str__(self):
        return f"{self.usuario} - {self.porcentaje_grasa}% en {self.fecha.date()}"


# También necesitarás actualizar el modelo Progreso
class Progreso(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="progresos"
    )
    fecha = models.DateField(auto_now_add=True)
    peso_actual = models.FloatField()
    grasa_estimada = models.FloatField()
    
    # Cambiar esta relación para apuntar a EvaluacionFisica
    evaluacion_referencia = models.ForeignKey(
        'EvaluacionFisica', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Evaluación física de referencia para este progreso"
    )
    
    nota = models.TextField(blank=True)

    def __str__(self):
        return f"Progreso de {self.usuario} - {self.fecha}"



class PlanEntrenamiento(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="planes_entrenamiento",
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
        related_name="planes_nutricion",
    )
    descripcion = models.TextField()
    calorias = models.IntegerField()
    macros = models.JSONField(null=True, blank=True)  # Proteínas, carbohidratos, grasas
    fecha_asignacion = models.DateTimeField(auto_now_add=True)




# Modelos actualizados para la comunidad
class CommunityPost(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name="posts_comunidad"
    )
    contenido = models.TextField(max_length=500)
    likes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def comments_count(self):
        return self.comentarios.count()
    



class PostLike(models.Model):
    """Modelo para manejar los likes de los posts"""
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    post = models.ForeignKey(
        CommunityPost,
        on_delete=models.CASCADE,
        related_name="post_likes"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'post')

    def __str__(self):
        return f"{self.usuario.username} likes {self.post.id}"


class PostComment(models.Model):
    """Modelo para los comentarios de los posts"""
    post = models.ForeignKey(
        CommunityPost,
        on_delete=models.CASCADE,
        related_name="comentarios"
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    contenido = models.TextField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comentario de {self.usuario.username} en post {self.post.id}"


class MensajeMotivacional(models.Model):
    texto = models.CharField(max_length=255)
    categoria = models.CharField(
        max_length=50
    ) 