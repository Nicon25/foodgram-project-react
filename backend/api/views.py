from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg, Q
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from foodgram.settings import ADMIN_EMAIL
from users.models import User, Follow
from recipes.models import Tag, Recipe, Ingredient, IngredientInRecipe, ShoppingCart, Favorites
#from .filters import TitleFilter
from .permissions import (IsAuthorOrReadOnly)
from .serializers import (ChangePasswordSerializer, CustomUserCreateSerializer, UserSerializer, FollowSerializer, TagSerializer, RecipeSerializer, IngredientSerializer, IngredientInRecipeSerializer, ShoppingCartSerializer, FavoritesSerializer)


# взял из api_yambd
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['list', 'create']:
            return [permissions.AllowAny()]  # Доступ для всех на просмотр юзеров и регистрации
        elif self.action == 'retrieve':
            return [permissions.IsAuthenticated()]  # Только авторизованные могут просматривать профили пользователей.
        elif self.action in ['set_password', 'me']:
            return [IsAuthorOrReadOnly()]  # Только владелец аккаунта может смены пароли и просматривать свой профиль
        else:
            return [permissions.IsAuthenticated()]  # По умолчанию, требуется авторизация

    def get_serializer_class(self):
        if self.action == 'set_password':
            return ChangePasswordSerializer # Сериализатор для смены пароля
        if self.action == 'create':
            return CustomUserCreateSerializer # Сериализатор на создание пользователя
        return UserSerializer # Сериализатор для работы с Users

    @action(methods=['post'], detail=False)
    def set_password(self, request):
        # Проверяем, что пользователь авторизован
        if not request.user.is_authenticated:
            return Response({'error': 'Пользователь не авторизован.'}, status=status.HTTP_401_UNAUTHORIZED)
        # Получаем текущего пользователя
        user = request.user
        # Получаем старый и новый пароль из данных запроса
        current_password = request.data.get('current_password', None)
        new_password = request.data.get('new_password', None)
        # Проверяем, что старый пароль соответствует текущему паролю пользователя
        if not user.check_password(current_password):
            return Response({'error': 'Неверный пароль.'}, status=status.HTTP_400_BAD_REQUEST)
        # Устанавливаем новый пароль
        user.set_password(new_password)
        user.save()
        return Response({'message': 'Пароль успешно изменен.'}, status=status.HTTP_200_OK)

    # Удаление токена
    @action(detail=False, methods=['post'])
    def logout(self, request):
        if IsAuthorOrReadOnly().has_object_permission(request, self, request.auth):
            request.auth.delete()
            return Response(status=204)
        else:
            return Response({'error': 'Доступ запрещен.'}, status=401)
        

class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class IngredientInRecipeViewSet(viewsets.ModelViewSet):
    queryset = IngredientInRecipe.objects.all()
    serializer_class = IngredientInRecipeSerializer


class ShoppingCartViewSet(viewsets.ModelViewSet):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer


class FavoritesViewSet(viewsets.ModelViewSet):
    queryset = Favorites.objects.all()
    serializer_class = FavoritesSerializer
