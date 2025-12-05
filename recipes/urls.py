# recipes/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from .api.views import (
    TaxonomyViewSet,
    FacetViewSet,
    TermViewSet,
    TermTreeViewSet,
    RecipeViewSet,
    RecipeTermViewSet,
)

app_name = "recipes"

router = DefaultRouter()
router.register("taxonomies", TaxonomyViewSet, basename="taxonomy")
router.register("facets", FacetViewSet, basename="facet")
router.register("terms", TermViewSet, basename="term")           # plano
router.register("terms-tree", TermTreeViewSet, basename="term-tree")  # árbol
router.register("recipes", RecipeViewSet, basename="recipe")
router.register("recipe-terms", RecipeTermViewSet, basename="recipeterm")

urlpatterns = [
    # Vistas HTML
    path("recipes/", views.recipe_list, name="recipe_list"),
    path("recipes/<slug:slug>/", views.recipe_detail, name="recipe_detail"),

    # API REST (JSON) generada por el router
    path("api/", include(router.urls)),
]