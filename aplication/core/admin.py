from django.contrib import admin
from aplication.core.models import *



@admin.register(Recomendacion)
class RecomendacionAdmin(admin.ModelAdmin):
    list_display = ('sexo', 'nombre', 'objetivo', 'porcentaje_min', 'porcentaje_max')
    search_fields = ('nombre', 'mensaje')
    list_filter = ('sexo', 'objetivo',)
    
    
@admin.register(EvaluacionFisica)
class EvaluacionFisicaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'fecha', 'porcentaje_grasa', 'recomendacion_msj')
    search_fields = ('usuario__username', 'recomendacion_msj__nombre')
    list_filter = ('recomendacion_msj',)
