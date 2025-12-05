from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404, render

from .models import Recipe, Facet, Term


def _get_descendant_term_ids(term_ids):
    """
    Dado un conjunto de IDs de términos seleccionados por el usuario,
    devuelve esos IDs + todos los IDs de sus descendientes (hijos, nietos, etc.).
    Esto permite que al filtrar por 'Postre' también se encuentren recetas
    etiquetadas solo con 'Pastel', 'Helado', etc.
    """
    expanded_ids = set(int(tid) for tid in term_ids)
    queue = list(expanded_ids)

    while queue:
        current_id = queue.pop()
        children = Term.objects.filter(parent_id=current_id).values_list("id", flat=True)
        for child_id in children:
            if child_id not in expanded_ids:
                expanded_ids.add(child_id)
                queue.append(child_id)

    return list(expanded_ids)


def recipe_list(request):
    """
    Lista de recetas con:
      - búsqueda por texto (?q=pollo)
      - filtros por facetas (?term=1&term=5...)
    """
    raw_term_ids = request.GET.getlist("term")
    query = request.GET.get("q", "").strip()

    recipes = Recipe.objects.all().prefetch_related("terms")

    # Búsqueda de texto
    if query:
        recipes = recipes.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(ingredients_text__icontains=query)
            | Q(instructions__icontains=query)
        )

    print('raw_term_ids', raw_term_ids,recipes, {recipes})
    # Filtro por términos (y sus descendientes)
    if raw_term_ids:
        # Expandir para incluir términos hijos
        selected_term_ids = _get_descendant_term_ids(raw_term_ids)
        recipes = recipes.filter(terms__id__in=selected_term_ids).distinct()

    facets = Facet.objects.prefetch_related(
        Prefetch("terms", queryset=Term.objects.order_by("order", "name"))
    ).order_by("order", "name")

    context = {
        "recipes": recipes,
        "facets": facets,
        "selected_term_ids": [int(pk) for pk in raw_term_ids],
        "query": query,
    }
    return render(request, "recipes/recipe_list.html", context)


def recipe_detail(request, slug: str):
    recipe = get_object_or_404(
        Recipe.objects.prefetch_related("terms__facet__taxonomy"),
        slug=slug,
    )

    # Agrupamos términos por faceta para mostrar las etiquetas
    facet_terms = {}
    for term in recipe.terms.all():
        facet_terms.setdefault(term.facet, []).append(term)

    context = {
        "recipe": recipe,
        "facet_terms": facet_terms,
    }
    return render(request, "recipes/recipe_detail.html", context)