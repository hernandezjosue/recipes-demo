# recipes/api/views.py
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from recipes.api.filters import RecipeFilter
from recipes.models import Taxonomy, Facet, Term, Recipe, RecipeTerm
from recipes.api.serializer import (
    TaxonomySerializer,
    FacetSerializer,
    TermSerializer,
    RecipeTermSerializer, TermTreeSerializer, RecipeListSerializer, RecipeDetailSerializer,
)


class TaxonomyViewSet(viewsets.ModelViewSet):
    queryset = Taxonomy.objects.all()
    serializer_class = TaxonomySerializer


class FacetViewSet(viewsets.ModelViewSet):
    queryset = Facet.objects.all().order_by("order","name")
    serializer_class = FacetSerializer

class TermTreeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Devuelve solo términos raíz, con sus hijos anidados recursivamente.
    Ideal para construir el árbol de filtros en el frontend.
    """
    queryset = Term.objects.filter(parent__isnull=True).order_by("facet", "order", "name")
    serializer_class = TermTreeSerializer


class TermViewSet(viewsets.ModelViewSet):
    queryset = Term.objects.all()
    serializer_class = TermSerializer



class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    lookup_field = 'slug'

    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        # Para el detalle (retrieve) usamos el serializer con facet_terms
        if self.action == "retrieve":
            return RecipeDetailSerializer
        # Para lista, create, update, etc., usamos el serializer simple
        return RecipeListSerializer


class RecipeTermViewSet(viewsets.ModelViewSet):
    queryset = RecipeTerm.objects.all()
    serializer_class = RecipeTermSerializer