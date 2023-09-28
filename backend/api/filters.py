from django_filters import rest_framework as filters
from recipes.models import Recipe
from rest_framework.filters import SearchFilter


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter(
        method="filter_is_favorited",
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method="filter_is_in_shopping_cart",
    )
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
        label='tags',
    )

    def filter_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(
                is_favorited__user=self.request.user
            )
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(
                is_in_shopping_cart__user=self.request.user
            )
        return queryset

    class Meta:
        model = Recipe
        fields = {
            "author",
            "tags",
            "is_favorited",
            "is_in_shopping_cart",
        }


class IngredientFilter(SearchFilter):
    search_param = 'name'
