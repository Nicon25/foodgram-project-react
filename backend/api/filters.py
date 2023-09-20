import django_filters
from recipes.models import Recipe


class RecipeFilter(django_filters.FilterSet):
    is_favorited = django_filters.BooleanFilter(
        field_name="is_favorited",
        method="filter_is_favorited",
    )
    is_in_shopping_cart = django_filters.BooleanFilter(
        field_name="is_in_shopping_cart",
        method="filter_is_in_shopping_cart",
    )

    def filter_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(is_favorited=True)
        return queryset.filter(is_favorited=False)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(is_in_shopping_cart=True)
        return queryset.filter(is_in_shopping_cart=False)

    class Meta:
        model = Recipe
        fields = {
            "author": ["exact"],
            "tags": ["exact"],
        }
