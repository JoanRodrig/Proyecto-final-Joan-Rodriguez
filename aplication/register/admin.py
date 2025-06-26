from django.contrib import admin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'sexo')
    search_fields = ('first_name', 'last_name', 'username')
    list_filter = ('sexo',)
    ordering = ['last_name'] 