from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg, Q
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

#from api_yamdb.settings import ADMIN_EMAIL
from users.models import User, Follow
from recipes.models import Tag, Recipe, Ingredient, IngredientInRecipe, ShoppingCart, Favorites
#from .filters import TitleFilter
# from .permissions import (IsAdminOrReadOnly,
#                           IsAuthorModeratorAdminOrReadOnlyPermission,
#                           IsRoleAdmin)
from .serializers import (UserSerializer, FollowSerializer, TagSerializer, RecipeSerializer, IngredientSerializer, IngredientInRecipeSerializer, ShoppingCartSerializer, FavoritesSerializer)


# взял из api_yambd
class UserViewSet(viewsets.ModelViewSet):
    """
    Доступ имеет только администратор
    /users/ - получить всех пользователей
    /users/{username}/ - управление пользователем с именем username
    /users/?search=username - поиск пользователя по имени username
    /users/me/ - показать текущего пользователя
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
#    serializer_class = AdminUserSerializer
#     permission_classes = (IsRoleAdmin,)
#     filter_backends = (filters.SearchFilter,)
#     lookup_field = 'username'
#     lookup_value_regex = r'[\w\@\.\+\-]+'
#     search_fields = ('username',)

#     def update(self, request, *args, **kwargs):
#         if request.method == 'PUT':
#             return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         partial = kwargs.pop('partial', False)
#         instance = self.get_object()
#         serializer = self.get_serializer(
#             instance, data=request.data, partial=partial
#         )
#         serializer.is_valid(raise_exception=True)
#         self.perform_update(serializer)
#         return Response(serializer.data)

#     @action(
#         detail=False, methods=['get', 'patch'],
#         url_path='me', url_name='me',
#         permission_classes=(IsAuthenticated,)
#     )
#     def about_me(self, request):
#         serializer = UserSerializer(request.user)
#         if request.method == 'PATCH':
#             serializer = UserSerializer(
#                 request.user, data=request.data, partial=True
#             )
#             serializer.is_valid(raise_exception=True)
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.data, status=status.HTTP_200_OK)


# def send_confirmation_code(user):
#     '''Отправка кода подверждения в email'''
#     confirmation_code = default_token_generator.make_token(user)
#     subject = 'Код подтверждения в API'
#     message = f'{confirmation_code} - Код для поддверждения авторизации в API'
#     admin_email = ADMIN_EMAIL
#     user_email = [user.email]
#     return send_mail(subject, message, admin_email, user_email)


# @api_view(['POST'])
# @permission_classes([AllowAny])
# def signup(request):
#     '''Регистрация нового пользователя'''
#     email = request.data.get('email')
#     username = request.data.get('username')

#     # Проверяем, существует ли пользователь с таким email или username
#     if (User.objects.filter(Q(email=email)).exists()
#             and not User.objects.filter(Q(username=username)).exists()):
#         return Response(
#             {'message': 'Пользователь с таким email уже зарегистрирован'},
#             status=status.HTTP_400_BAD_REQUEST
#         )
#     # Проверяем, если в запросе содержится username
#     # зарегистрированного пользователя и несоответствующий ему email
#     if User.objects.filter(Q(username=username) & ~Q(email=email)).exists():
#         return Response(
#             {'message': 'Пользователь с таким email уже зарегистрирован'},
#             status=status.HTTP_400_BAD_REQUEST
#         )

#     # Проверяем, существует ли пользователь с таким email или username
#     if User.objects.filter(Q(email=email) | Q(username=username)).exists():
#         user = User.objects.get(Q(email=email) | Q(username=username))
#         send_confirmation_code(user)  # Отправляем новый confirmation code
#         return Response(
#             {'message': 'Новый confirmation code отправлен на почту'},
#             status=status.HTTP_200_OK
#         )

#     # Если пользователь не существует, регистрируем нового
#     serializer = RegistrationSerializer(data=request.data)
#     if serializer.is_valid():
#         user = serializer.save()
#         send_confirmation_code(user)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
