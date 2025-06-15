from django.contrib import admin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'fecha_nacimiento', 'sexo')
    search_fields = ('first_name', 'last_name', 'username')
    list_filter = ('sexo',)
    ordering = ['last_name'] 