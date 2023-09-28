from django.contrib import admin

from .models import (Favorites, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingCart, Tag)


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'cooking_time',
        'text', 'author', 'favorites_count'
    )
    list_filter = ('name', 'author', 'tags')

    def favorites_count(self, object):
        return object.is_favorited.count()


class IngredientAdmin(admin.ModelAdmin):
    list_filter = ('name',)


admin.site.register(Tag)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientInRecipe)
admin.site.register(ShoppingCart)
admin.site.register(Favorites)
