"""
Utilidades para manejo de archivos y uploads en la aplicación de recetas.
Sigue el principio de Single Responsibility (SOLID).
"""
import os
import uuid
from datetime import datetime
from django.utils.text import slugify


def sanitize_filename(filename: str) -> str:
    """
    Limpia un nombre de archivo removiendo caracteres problemáticos.

    Args:
        filename: Nombre original del archivo

    Returns:
        Nombre sanitizado sin caracteres especiales
    """
    name, ext = os.path.splitext(filename)
    # Remueve espacios, convierte a minúsculas y usa slugify para limpiar
    clean_name = slugify(name.replace('_', '-'))
    # Limpia la extensión también
    clean_ext = ext.lower().replace(' ', '')
    return f"{clean_name}{clean_ext}"


def generate_recipe_image_filename(instance, original_filename: str) -> str:
    """
    Genera un nombre único y seguro para imágenes de recetas.

    Estrategia:
    - Usa el slug de la receta (o título sanitizado)
    - Agrega timestamp para unicidad
    - Preserva la extensión original sanitizada
    - Organiza en subdirectorios por año/mes

    Args:
        instance: Instancia del modelo Recipe
        original_filename: Nombre original del archivo subido

    Returns:
        Ruta completa para el archivo: recipes/YYYY/MM/recipe-slug-timestamp.ext

    Example:
        >>> generate_recipe_image_filename(recipe, "Screenshot_2025-12-06_at_11.28.16a.m..png")
        'recipes/2025/12/pastel-de-chocolate-20251206112816-a1b2c3.png'
    """
    # Obtener extensión sanitizada
    ext = os.path.splitext(original_filename)[1].lower().replace(' ', '')
    if not ext:
        ext = '.jpg'  # Extensión por defecto

    # Generar nombre base desde el título o slug
    if instance.slug:
        base_name = instance.slug
    elif instance.title:
        base_name = slugify(instance.title)
    else:
        base_name = 'recipe'

    # Timestamp para unicidad
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

    # UUID corto para garantizar unicidad absoluta
    unique_id = uuid.uuid4().hex[:6]

    # Organizar por año/mes para mejor gestión de archivos
    date_path = datetime.now().strftime('%Y/%m')

    # Construir nombre final
    filename = f"{base_name}-{timestamp}-{unique_id}{ext}"

    return os.path.join('recipes', date_path, filename)


def generate_generic_image_filename(subdirectory: str, prefix: str = 'image'):
    """
    Factory function para generar funciones de renombrado genéricas.
    Útil para otros modelos que necesiten subir imágenes.

    Args:
        subdirectory: Subdirectorio donde guardar (ej: 'products', 'users')
        prefix: Prefijo para el nombre del archivo

    Returns:
        Función callable para usar en upload_to

    Example:
        upload_to=generate_generic_image_filename('products', 'product')
    """
    def _upload_to(instance, filename: str) -> str:
        ext = os.path.splitext(filename)[1].lower()
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        unique_id = uuid.uuid4().hex[:8]
        date_path = datetime.now().strftime('%Y/%m')
        filename = f"{prefix}-{timestamp}-{unique_id}{ext}"
        return os.path.join(subdirectory, date_path, filename)

    return _upload_to
