from django.contrib import admin
from aplication.core.models import *

# Register your models here.
""" 
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'fecha_nacimiento', 'sexo')
    search_fields = ('first_name', 'last_name', 'Username')
    list_filter = ('sexo')
    ordering = ['apellidos']
    """
    
@admin.register(EvaluacionFisica)
class EvaluacionFisicaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'fecha', 'porcentaje_grasa')
    search_fields = ('usuario__username',)
