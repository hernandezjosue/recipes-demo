from django.db import models
from django.utils.text import slugify


# Create your models here.
# recipes/models.py


class Taxonomy(models.Model):
    """
    Conjunto de facetas coherentes.
    Ejemplos:
      - 'Taxonomía principal de recetas'
      - 'Connotación emocional de platos'
    """
    name = models.CharField("Nombre de la taxonomía", max_length=100, unique=True)

    class Meta:
        verbose_name = "Taxonomía"
        verbose_name_plural = "Taxonomías"

    def __str__(self) -> str:
        return self.name


class Facet(models.Model):
    """
    Dimensión de clasificación dentro de una taxonomía.
    Ejemplos: 'Tipo de plato', 'Ingrediente principal', 'Técnica de cocción'.
    """
    taxonomy = models.ForeignKey(
        Taxonomy,
        on_delete=models.CASCADE,
        related_name="facets",
    )
    name = models.CharField("Nombre de la faceta", max_length=100)
    description = models.CharField(
        "Descripción",
        max_length=255,
        blank=True,
    )
    order = models.PositiveIntegerField(
        "Orden de visualización",
        default=0,
        help_text="Número para ordenar las facetas en la interfaz.",
    )

    class Meta:
        verbose_name = "Faceta"
        verbose_name_plural = "Facetas"
        unique_together = ("taxonomy", "name")
        ordering = ("order", "name")

    def __str__(self) -> str:
        return f"{self.taxonomy}: {self.name}"


class Term(models.Model):
    """
    Término dentro de una faceta (lo que en tus diapositivas son las etiquetas tipo:
    'Postre', 'Horneado', 'Piña', 'Pastel', etc.)
    Permite jerarquía (padre/hijo) para representar árboles.
    """
    facet = models.ForeignKey(
        Facet,
        on_delete=models.CASCADE,
        related_name="terms",
    )
    name = models.CharField("Nombre del término", max_length=100)
    description = models.CharField(
        "Descripción",
        max_length=255,
        blank=True,
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        help_text="Término padre (opcional) para crear jerarquías.",
    )
    order = models.PositiveIntegerField(
        "Orden de visualización",
        default=0,
    )

    class Meta:
        verbose_name = "Término"
        verbose_name_plural = "Términos"
        unique_together = ("facet", "name", "parent")
        ordering = ("facet", "parent__id", "order", "name")

    def __str__(self) -> str:
        if self.parent:
            return f"{self.facet.name} > {self.parent.name} > {self.name}"
        return f"{self.facet.name} > {self.name}"


class Recipe(models.Model):
    """
    Equivalente de 'Objeto' en tu esquema, pero específico para recetas de cocina.
    """
    title = models.CharField("Título", max_length=200)
    slug = models.SlugField(
        "Slug",
        max_length=250,
        unique=True,
        null=True,  # <- permitir nulos en la base de datos
        blank=True,  # <- permitir dejarlo vacío en formularios
        help_text="URL amigable generada automáticamente desde el título.",
    )
    description = models.TextField(
        "Descripción breve",
        blank=True,
        help_text="Resumen de la receta o notas generales.",
    )
    instructions = models.TextField(
        "Instrucciones",
        help_text="Texto libre con los pasos de la receta.",
    )
    ingredients_text = models.TextField(
        "Ingredientes",
        help_text="Lista de ingredientes en texto libre.",
    )
    image = models.ImageField(
        "Imagen principal",
        upload_to="recipes/",
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Relación N a N con Term (Termino_has_Objeto)
    terms = models.ManyToManyField(
        Term,
        through="RecipeTerm",
        related_name="recipes",
        blank=True,
    )

    class Meta:
        verbose_name = "Receta"
        verbose_name_plural = "Recetas"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Recipe.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title


class RecipeTerm(models.Model):
    """
    Tabla intermedia equivalente a Termino_has_Objeto.
    """
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Etiqueta de receta"
        verbose_name_plural = "Etiquetas de receta"
        unique_together = ("recipe", "term")

    def __str__(self) -> str:
        return f"{self.recipe} – {self.term}"
