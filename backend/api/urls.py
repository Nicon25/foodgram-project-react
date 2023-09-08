from django.urls import include, path
from rest_framework import routers

from .views import (UserViewSet, FollowViewSet, TagViewSet, RecipeViewSet, IngredientViewSet, IngredientInRecipeViewSet, ShoppingCartViewSet, FavoritesViewSet) #, signup, Token)

# взял из api_yambd

v1_router = routers.DefaultRouter()
v1_router.register(r'follows', FollowViewSet, basename='follows')
v1_router.register(r'tags', TagViewSet, basename='tags')
v1_router.register(r'recipes', RecipeViewSet, basename='recipes')
v1_router.register(r'ingredients', IngredientViewSet, basename='ingredients')
v1_router.register(r'ingredientsinrecipes', IngredientInRecipeViewSet, basename='ingredientsinrecipes')
v1_router.register(r'shoppingcart', ShoppingCartViewSet, basename='shoppingcart')
v1_router.register(r'favorites', FavoritesViewSet, basename='favorites')
# v1_router.register(r'titles/(?P<title_id>\d+)/reviews',
#                    ReviewViewSet, basename='reviews')
# v1_router.register(
#     r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
#     CommentViewSet, basename='comments'
# )
v1_router.register(r'users', UserViewSet, basename='users')
# v1_auth_path = [
#     path('signup/', signup, name='signup'),
#     path('token/', Token.as_view(), name='token')
# ]

urlpatterns = [
    path('', include(v1_router.urls)),
    # path('v1/auth/', include(v1_auth_path))
]
