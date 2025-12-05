from rest_framework import serializers

from recipes.models import Taxonomy, Facet, Term, Recipe, RecipeTerm


class TaxonomySerializer(serializers.ModelSerializer):
    class Meta:
        model = Taxonomy
        fields = "__all__"


class FacetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Facet
        fields = "__all__"


class TermSerializer(serializers.ModelSerializer):
    #children = serializers.SerializerMethodField()
    class Meta:
        model = Term
        fields = "__all__"

    #def get_children(self, obj):
        #qs = obj.children.all().order_by("order", "name")
        #return TermSerializer(qs, many=True).data
        # Hijos directos; si quieres árbol más profundo se puede hacer recursivo
        #return TermSerializer(obj.children.all().order_by("order", "name"), many=True).data

class TermTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Term
        # no hace falta repetir facet/parent en cada nivel si no quieres,
        # pero los dejamos por si el frontend los usa
        fields = ["id", "name", "description", "order", "facet", "parent", "children"]

    def get_children(self, obj):
        qs = obj.children.all().order_by("order", "name")
        return TermTreeSerializer(qs, many=True).data

class RecipeListSerializer(serializers.ModelSerializer):
    """
    Serializer para la lista de recetas (sin facet_terms).
    """
    class Meta:
        model = Recipe
        fields = "__all__"


class RecipeDetailSerializer(serializers.ModelSerializer):
    """
    Serializer para el detalle de una receta, incluye facet_terms.
    """
    facet_terms = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = "__all__"  # incluye todos los campos + facet_terms

    def get_facet_terms(self, obj):
        """
        Agrupa los términos de la receta por faceta,
        igual que haces en la vista HTML de detalle.
        """
        groups = {}

        for term in obj.terms.select_related("facet"):
            facet = term.facet
            if facet.id not in groups:
                groups[facet.id] = {
                    "facet_id": facet.id,
                    "facet_name": facet.name,
                    "terms": [],
                }
            groups[facet.id]["terms"].append(
                {
                    "id": term.id,
                    "name": term.name,
                }
            )

        return list(groups.values())




class RecipeTermSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeTerm
        fields = "__all__"