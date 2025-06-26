# CONFIGURACION CHOICES
SEX_CHOICES=[('M', 'Masculino'), ('F', 'Femenino')]



OBJETIVO_CHOICES = [
        ("perder_grasa", "Perder grasa"),
        ("tonificar", "Tonificar"),
        ("ganar_musculo", "Ganar músculo"),
        ("salud_general", "Mejorar salud general"),
    ]

# const.py

# Tamaños de archivo
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB en bytes

# Extensiones válidas para imágenes
VALID_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp']

# Configuración de gráficos
GRAFICO_CONFIG = {
    'figsize': (10, 6),
    'dpi': 150,
    'color': '#2E8B57',
    'linewidth': 2,
    'markersize': 6,
    'grid_alpha': 0.3,
    'max_fechas_sin_rotar': 10,
}

# Mensajes de error
ERROR_MESSAGES = {
    'archivo_vacio': 'El archivo está vacío',
    'archivo_grande': 'El archivo es demasiado grande. Máximo {max_size:.1f} MB',
    'formato_invalido': 'Formato no válido. Formatos permitidos: {extensions}',
    'imagen_invalida': 'El archivo no es una imagen válida',
    'sin_datos': 'No hay datos suficientes para generar el gráfico',
    'error_db': 'Error al acceder a los datos',
    'error_interno': 'Error interno del sistema',
}
