from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date
from mysite.const import SEX_CHOICES
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from aplication.core.utils import validate_image_file


# Create your models here.


class Usuario(AbstractUser):
    edad = models.PositiveIntegerField(null=True, blank=True)

    sexo = models.CharField(max_length=1, null=True , choices=SEX_CHOICES, verbose_name="Sexo")

    fecha_nacimiento = models.DateField(
        verbose_name="Fecha de Nacimiento", null=True, blank=True
    )

    foto = models.ImageField(
        upload_to='usuarios/', 
        verbose_name="Foto", 
        null=True, 
        blank=True,
        validators=[validate_image_file]
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

    class Meta:
        ordering = ["last_name", "first_name"]
        indexes = [models.Index(fields=["last_name"])]
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    @property
    def nombre_completo(self):
        return f"{self.last_name} {self.first_name}"
    
    def __str__(self):
        return self.nombre_completo or self.username

    def get_image(self):
        if self.foto:
            return self.foto.url
        else:
            return "/static/img/usuario_anonimo.png"
        
    def clean(self):
        """Validaciones personalizadas del modelo"""
        super().clean()
        
        # Validar fecha de nacimiento
        if self.fecha_nacimiento:
            if self.fecha_nacimiento > date.today():
                raise ValidationError({
                    'fecha_nacimiento': 'La fecha de nacimiento no puede ser futura.'
                })
            
            edad_calculada = self.calcular_edad(self.fecha_nacimiento)
            if edad_calculada < 13:
                raise ValidationError({
                    'fecha_nacimiento': 'Debe ser mayor de 13 años para registrarse.'
                })
        
    def save(self, *args, **kwargs):
        """Sobrescribe save para calcular edad automáticamente"""
        # Limpiar y capitalizar nombres
        if self.first_name:
            self.first_name = self.first_name.strip().title()
        if self.last_name:
            self.last_name = self.last_name.strip().title()
            
        # Calcular edad si hay fecha de nacimiento
        if self.fecha_nacimiento:
            self.edad = self.calcular_edad(self.fecha_nacimiento)
            
        # Validar antes de guardar
        if not self.is_superuser:
            self.full_clean()
        super().save(*args, **kwargs)

    @staticmethod
    def calcular_edad(fecha_nacimiento):
        if not fecha_nacimiento:
            return None
            
        today = date.today()
        return today.year - fecha_nacimiento.year - (
            (today.month, today.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
        )
