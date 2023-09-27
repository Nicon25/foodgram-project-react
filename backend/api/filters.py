import django_filters
from recipes.models import Recipe


class RecipeFilter(django_filters.FilterSet):
    is_favorited = django_filters.BooleanFilter(
        method="filter_is_favorited",
    )
    is_in_shopping_cart = django_filters.BooleanFilter(
        method="filter_is_in_shopping_cart",
    )
    tags = django_filters.AllValuesMultipleFilter(
        field_name='tags__slug',
        label='tags',
    )

    def filter_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(
                favorite__user=self.request.user
            )
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(
                shoppingcart__user=self.request.user
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
