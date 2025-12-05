# recipes/api/filters.py
import django_filters
from django.db import models

from recipes.models import Recipe, Term


def get_descendant_term_ids(root_ids: list[int]) -> list[int]:
    """
    Dado un conjunto de IDs de términos raíz, devuelve esos IDs
    + todos los descendientes (hijos, nietos, etc.).

    Se mantiene independiente del FilterSet (SRP).
    """
    expanded_ids: set[int] = set(int(tid) for tid in root_ids)
    queue: list[int] = list(expanded_ids)

    # Para reducir queries, precalculamos todas las relaciones parent->children
    # en memoria cuando hay varios términos.
    children_map: dict[int, list[int]] = {}

    # Solo si hay más de un id, tiene sentido precargar:
    if expanded_ids:
        for parent_id, child_id in Term.objects.filter(
            parent_id__in=expanded_ids
        ).values_list("parent_id", "id"):
            children_map.setdefault(parent_id, []).append(child_id)

    while queue:
        current_id = queue.pop()

        # Si no está en el mapa (aún), cargamos on-demand sus hijos
        if current_id not in children_map:
            children = list(
                Term.objects.filter(parent_id=current_id).values_list("id", flat=True)
            )
            children_map[current_id] = children

        for child_id in children_map[current_id]:
            if child_id not in expanded_ids:
                expanded_ids.add(child_id)
                queue.append(child_id)

    return list(expanded_ids)


class RecipeFilter(django_filters.FilterSet):
    """
    Filtros para Recipe:
      - q: búsqueda de texto
      - term: términos de taxonomía (con expansión a descendientes)
    """

    q = django_filters.CharFilter(method="filter_q")
    term = django_filters.ModelMultipleChoiceFilter(
        method="filter_term",
        field_name="terms__id",
        to_field_name="id",
        queryset=Term.objects.all(),
    )

    class Meta:
        model = Recipe
        fields = ["q", "term"]

    def filter_q(self, queryset, name, value):
        """
        /api/recipes/?q=pollo

        Busca el texto en título, descripción, ingredientes e instrucciones.
        """
        value = (value or "").strip()
        if not value:
            return queryset

        query = (
            models.Q(title__icontains=value)
            | models.Q(description__icontains=value)
            | models.Q(ingredients_text__icontains=value)
            | models.Q(instructions__icontains=value)
        )
        return queryset.filter(query)

    def filter_term(self, queryset, name, value):
        """
        /api/recipes/?term=3&term=4

        value llega como una lista de objetos Term seleccionados.
        Expandimos a hijos para respetar la jerarquía
        (Postre => Postre + pastel + panque ...).
        """
        if not value:
            return queryset

        root_ids = [term.id for term in value]
        expanded_ids = get_descendant_term_ids(root_ids)

        return queryset.filter(terms__id__in=expanded_ids).distinct()