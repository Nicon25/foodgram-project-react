from django.contrib import admin

from .models import Tag, Recipe, Ingredient, IngredientInRecipe, ShoppingCart, Favorites

admin.site.register(Tag)
admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(IngredientInRecipe)
admin.site.register(ShoppingCart)
admin.site.register(Favorites)