# BodyScanner IA – Sistema Automatizado de Evaluación Física

## Integrantes
- Kevin Ernesto Barboza Cargua  
- Joan Martin Rodríguez Cruz  
- Enzo Rafael Parra Bonifaz  

## Instrucciones de instalación y ejecución

1. **Clonar el repositorio**  

    git clone https://github.com/tu_usuario/bodyscanner-ia.git
    cd bodyscanner-ia


2. **Crear y activar un entorno virtual**

    python -m venv venv
    venv\Scripts\activate



3. **Instalar dependencias**

    pip install -r requirements.txt



4.  **Configurar la base de datos**
Ajusta en settings.py las credenciales de tu base (por defecto usa SQLite).

    python manage.py migrate


5. **Ejecutar el servidor de desarrollo**

    python manage.py runserver


6. **Abrir en el navegador**

Visita: http://127.0.0.1:8000


**Breve descripción de funcionalidades**
•	Análisis corporal con IA: sube o captura una foto de cuerpo entero para estimar porcentaje de grasa corporal usando visión por computadora y modelos entrenados.
•	Planes personalizados: genera automáticamente rutinas de ejercicio y dietas adaptadas al perfil y objetivos del usuario.
•	Seguimiento de progreso: guarda evaluaciones periódicas y muestra la evolución visual y numérica del usuario.
•	Comunidad y motivación: foro interno para compartir avances y mensajes motivacionales.

