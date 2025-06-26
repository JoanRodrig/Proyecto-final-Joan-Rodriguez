# validators.py
import os
import logging
from PIL import Image
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from mysite.const import MAX_FILE_SIZE, VALID_IMAGE_EXTENSIONS

# Configurar logger
logger = logging.getLogger(__name__)

class ImageValidationError(ValidationError):
    """Excepción personalizada para errores de validación de imágenes."""
    pass

def validate_image_file(value):
    """
    Validador completo para archivos de imagen con manejo robusto de errores.
    
    Args:
        value: Archivo subido
        
    Raises:
        ImageValidationError: Si la validación falla
    """
    if not value:
        return
        
    try:
        # Validar que el archivo tiene nombre
        if not hasattr(value, 'name') or not value.name:
            logger.warning("Archivo sin nombre proporcionado")
            raise ImageValidationError(_('Archivo inválido: sin nombre'))
            
        # Validar extensión
        try:
            ext = os.path.splitext(value.name)[1].lower()
            if ext not in VALID_IMAGE_EXTENSIONS:
                logger.warning(f"Extensión inválida: {ext}")
                raise ImageValidationError(
                    _('Formato no válido. Formatos permitidos: %(extensions)s'),
                    params={'extensions': ', '.join(VALID_IMAGE_EXTENSIONS)},
                )
        except (AttributeError, TypeError) as e:
            logger.error(f"Error procesando nombre de archivo: {e}")
            raise ImageValidationError(_('Nombre de archivo inválido'))
            
        # Validar tamaño
        try:
            if not hasattr(value, 'size'):
                logger.error("Archivo sin atributo 'size'")
                raise ImageValidationError(_('No se puede determinar el tamaño del archivo'))
                
            if value.size <= 0:
                logger.warning("Archivo vacío")
                raise ImageValidationError(_('El archivo está vacío'))
                
            if value.size > MAX_FILE_SIZE:
                max_size_mb = MAX_FILE_SIZE / (1024 * 1024)
                logger.warning(f"Archivo demasiado grande: {value.size} bytes")
                raise ImageValidationError(
                    _('El archivo es demasiado grande. Tamaño máximo: %(max_size).1f MB'),
                    params={'max_size': max_size_mb},
                )
        except (AttributeError, TypeError) as e:
            logger.error(f"Error validando tamaño de archivo: {e}")
            raise ImageValidationError(_('Error al validar el tamaño del archivo'))
            
        # Validar que sea realmente una imagen
        try:
            # Guardar posición actual del archivo
            current_position = value.tell() if hasattr(value, 'tell') else 0
            
            # Intentar abrir como imagen
            image = Image.open(value)
            image.verify()
            
            # Restaurar posición del archivo
            if hasattr(value, 'seek'):
                value.seek(current_position)
                
            logger.debug(f"Imagen válida: {value.name}, formato: {image.format}")
            
        except (IOError, OSError) as e:
            logger.warning(f"Archivo no es una imagen válida: {e}")
            raise ImageValidationError(_('El archivo no es una imagen válida'))
        except Exception as e:
            logger.error(f"Error inesperado validando imagen: {e}")
            raise ImageValidationError(_('Error al validar la imagen'))
            
    except ImageValidationError:
        # Re-lanzar errores de validación
        raise
    except Exception as e:
        # Capturar cualquier error inesperado
        logger.error(f"Error inesperado en validate_image_file: {e}")
        raise ImageValidationError(_('Error inesperado al validar el archivo'))

def validate_image_size(value):
    """
    Validador específico para el tamaño de imagen.
    
    Args:
        value: Archivo subido
        
    Raises:
        ValidationError: Si el tamaño excede el límite
    """
    try:
        if not value:
            return
            
        if not hasattr(value, 'size'):
            logger.error("Archivo sin atributo 'size' en validate_image_size")
            raise ValidationError(_('No se puede determinar el tamaño del archivo'))
            
        if value.size > MAX_FILE_SIZE:
            max_size_mb = MAX_FILE_SIZE / (1024 * 1024)
            logger.warning(f"Archivo excede tamaño máximo: {value.size} bytes")
            raise ValidationError(
                _('El archivo es demasiado grande. Máximo %(max_size).1f MB.'),
                params={'max_size': max_size_mb}
            )
            
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error inesperado en validate_image_size: {e}")
        raise ValidationError(_('Error al validar el tamaño del archivo'))