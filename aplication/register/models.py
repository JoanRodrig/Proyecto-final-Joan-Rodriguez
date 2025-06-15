from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date
from mysite.const import SEX_CHOICES


# Create your models here.


class Usuario(AbstractUser):
    edad = models.PositiveIntegerField(null=True, blank=True)
    
    sexo = models.CharField(max_length=1, choices=SEX_CHOICES, verbose_name="Sexo")
    
    fecha_nacimiento = models.DateField(verbose_name="Fecha de Nacimiento", null=True, blank=True)
    
    foto = models.ImageField(upload_to='usuarios/', verbose_name="Foto", null=True, blank=True)
    
    altura_cm = models.FloatField(null=True, blank=True)
    
    peso_kg = models.FloatField(null=True, blank=True)
    
    


class Meta:
    # Define el orden predeterminado de los usuario por nombre
    ordering = ['apellidos']
    indexes = [models.Index(fields=['apellidos'])]
    # Nombre en singular y plural del modelo en la interfaz de administración
    verbose_name = "Usuario"
    verbose_name_plural = "Usuarios"
    
    
    @property
    def nombre_completo(self):
        return f"{self.apellidos} {self.nombres}"
    
    def __str__(self):
        return self.nombres

    def get_image(self):
        if self.foto:
            return self.foto.url
        else:
            return '/static/img/usuario_anonimo.png'

    def save(self, *args, **kwargs):
        if self.fecha_nacimiento:
            self.edad = self.calcular_edad(self.fecha_nacimiento)
        super().save(*args, **kwargs)


    @staticmethod
    def calcular_edad(fecha_nacimiento):    
        return date.today().year - fecha_nacimiento.year - (
            (date.today().month, date.today().day) < (fecha_nacimiento.month, fecha_nacimiento.day)
        )


    @staticmethod   
    def cantidad_usuarios():
        return Usuario.objects.all().count()