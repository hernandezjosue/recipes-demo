from django.contrib import admin

# Register your models here.
# recipes/admin.py
from django.contrib import admin
from .models import Taxonomy, Facet, Term, Recipe, RecipeTerm


class TermInline(admin.TabularInline):
    model = Term
    extra = 1


@admin.register(Taxonomy)
class TaxonomyAdmin(admin.ModelAdmin):
    list_display = ("name",)
    #inlines = [TermInline]


@admin.register(Facet)
class FacetAdmin(admin.ModelAdmin):
    list_display = ("name", "taxonomy", "order")
    list_filter = ("taxonomy",)
    search_fields = ("name", "description")
    inlines = [TermInline]


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ("name", "facet", "parent", "order")
    list_filter = ("facet",)
    search_fields = ("name", "description")


class RecipeTermInline(admin.TabularInline):
    model = RecipeTerm
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "created_at", "updated_at")
    search_fields = ("title", "description", "ingredients_text", "instructions")
    exclude = ("slug",)  # Oculta el campo slug en el formulario
    inlines = [RecipeTermInline]


@admin.register(RecipeTerm)
class RecipeTermAdmin(admin.ModelAdmin):
    list_display = ("recipe", "term")
    list_filter = ("term__facet", "term__facet__taxonomy")