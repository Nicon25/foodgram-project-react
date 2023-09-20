from django.urls import include, path
from rest_framework import routers

from .views import IngredientViewSet, RecipeViewSet, TagViewSet, UserViewSet

v1_router = routers.DefaultRouter()
v1_router.register(r"tags", TagViewSet, basename="tags")
v1_router.register(r"recipes", RecipeViewSet, basename="recipes")
v1_router.register(r"ingredients", IngredientViewSet, basename="ingredients")
v1_router.register(r"users", UserViewSet, basename="users")

urlpatterns = [
    path("", include(v1_router.urls)),
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]
