from django.urls import include, path
from rest_framework import routers

from .views import (UserViewSet, FollowViewSet, TagViewSet, RecipeViewSet, IngredientViewSet, IngredientInRecipeViewSet, FavoritesViewSet) #, signup, Token)

# взял из api_yambd

v1_router = routers.DefaultRouter()
v1_router.register(r'follows', FollowViewSet, basename='follows')
v1_router.register(r'tags', TagViewSet, basename='tags')
v1_router.register(r'recipes', RecipeViewSet, basename='recipes')
v1_router.register(r'ingredients', IngredientViewSet, basename='ingredients')
v1_router.register(r'ingredientsinrecipes', IngredientInRecipeViewSet, basename='ingredientsinrecipes')
v1_router.register(r'favorites', FavoritesViewSet, basename='favorites')
v1_router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(v1_router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
