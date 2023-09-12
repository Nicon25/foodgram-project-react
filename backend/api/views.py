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
from .permissions import (IsOwner)
from .serializers import (ChangePasswordSerializer, UserSerializer, FollowSerializer, TagSerializer, RecipeSerializer, IngredientSerializer, IngredientInRecipeSerializer, ShoppingCartSerializer, FavoritesSerializer)


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
            return [IsOwner()]  # Только владелец аккаунта может смены пароли и просматривать свой профиль
        else:
            return [permissions.IsAuthenticated()]  # По умолчанию, требуется авторизация

    # Установка нового пароля
    @action(detail=False, methods=['post'])
    def set_password(self, request):
        user = self.request.user
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            if user.check_password(serializer.validated_data['old_password']):
                user.set_password(serializer.validated_data['new_password'])
                user.save()
                return Response({'message': 'Пароль успешно изменен.'}, status=204)
            else:
                return Response({'error': 'Старый пароль введен не верно.'}, status=400)
        return Response(serializer.errors, status=400)

    # Удаление токена
    @action(detail=False, methods=['post'])
    def logout(self, request):
        if IsOwner().has_object_permission(request, self, request.auth):
            request.auth.delete()
            return Response(status=204)
        else:
            return Response({'error': 'Доступ запрещен.'}, status=401)
        
# class Token(APIView):
#     def post(self, request):
#         serializer = ObtainTokenSerializer(data=request.data)
#         if serializer.is_valid():
#             username = serializer.data['username']
#             confirmation_code = serializer.data['confirmation_code']
#             user = get_object_or_404(User, username=username)
#             if confirmation_code != user.confirmation_code:
#                 return Response(
#                     serializer.errors,
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#             token = RefreshToken.for_user(user)
#             return Response(
#                 {'token': str(token.access_token)},
#                 status=status.HTTP_200_OK
#             )
#         return Response(
#             serializer.errors,
#             status=status.HTTP_400_BAD_REQUEST
#         )


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    # permission_classes = (IsAdminOrReadOnly,)
    # filter_backends = (SearchFilter, )
    # search_fields = ('name', )
    # lookup_field = 'slug'


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
