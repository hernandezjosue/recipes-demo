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
    """
    Serializer recursivo para representar términos con sus hijos.
    Solo incluye información relevante del término (sin facet/parent redundante).
    Cumple SRP: responsable únicamente de serializar la jerarquía de términos.
    """
    children = serializers.SerializerMethodField()

    class Meta:
        model = Term
        fields = ["id", "name", "description", "order", "children"]

    def get_children(self, obj):
        """Obtiene hijos ordenados recursivamente."""
        qs = obj.children.all().order_by("order", "name")
        return TermTreeSerializer(qs, many=True).data


class FacetTermsTreeSerializer(serializers.ModelSerializer):
    """
    Serializer que agrupa términos jerárquicos por faceta.
    Cumple OCP: puede extenderse sin modificar TermTreeSerializer.
    FacetTermsTreeSerializer toma una caja (Faceta), encuentra los
    juguetes principales (términos raíz), y le pide a su ayudante (TermTreeSerializer)
    que traiga también todos los juguetes hijos recursivamente"
    """
    terms = serializers.SerializerMethodField()

    class Meta:
        model = Facet
        fields = ["id", "name", "description", "order", "terms"]

    def get_terms(self, obj):
        """
        Devuelve solo los términos raíz de esta faceta con sus hijos anidados.
        Delegación de responsabilidad a TermTreeSerializer (SRP).
        """
        root_terms = obj.terms.filter(parent__isnull=True).order_by("order", "name")
        return TermTreeSerializer(root_terms, many=True).data

class RecipeListSerializer(serializers.ModelSerializer):
    """
    Serializer para la lista de recetas (sin facet_terms).
    """
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = "__all__"

    def get_image(self, obj):
        """
        Devuelve la URL completa de la imagen usando request.build_absolute_uri
        para que funcione correctamente con Next.js Image Optimization.
        """
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class RecipeDetailSerializer(serializers.ModelSerializer):
    """
    Serializer para el detalle de una receta, incluye facet_terms.
    """
    image = serializers.SerializerMethodField()
    facet_terms = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = "__all__"  # incluye todos los campos + facet_terms

    def get_image(self, obj):
        """
        Devuelve la URL completa de la imagen usando request.build_absolute_uri
        para que funcione correctamente con Next.js Image Optimization.
        """
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

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