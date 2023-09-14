from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer

from users.models import User, Follow
from recipes.models import Tag, Recipe, Ingredient, IngredientInRecipe, Favorites
import base64

from django.core.files.base import ContentFile

# взял из api_yambd
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('email', 'username', 'first_name', 'last_name', 'password')
        model = User

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    

class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


class ChangePasswordSerializer(serializers.Serializer):
    class Meta:
        fields = ('current_password', 'new_password')
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['current_password'] == data['new_password']:
            raise serializers.ValidationError('Новый пароль должен отличаться от старого.')
        return data


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('__all__')
        model = Follow


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        # Если полученный объект строка, и эта строка 
        # начинается с 'data:image'...
        if isinstance(data, str) and data.startswith('data:image'):
            # ...начинаем декодировать изображение из base64.
            # Сначала нужно разделить строку на части.
            format, imgstr = data.split(';base64,')  
            # И извлечь расширение файла.
            ext = format.split('/')[-1]  
            # Затем декодировать сами данные и поместить результат в файл,
            # которому дать название по шаблону.
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)

class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)
    author = serializers.CharField(read_only=True)
    class Meta:
        fields = ('__all__')
        model = Recipe


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('__all__')
        model = Ingredient

    
class IngredientInRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('__all__')
        model = IngredientInRecipe


class FavoritesSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('__all__')
        model = Favorites

# class AdminUserSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = User
#         fields = (
#             'username', 'email', 'first_name', 'last_name', 'bio', 'role',
#         )

#     def validate_username(self, value):
#         if value == 'me':
#             raise serializers.ValidationError(
#                 'Имя пользователя "me" не разрешено.'
#             )
#         return value


# class CategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         fields = ('name', 'slug')
#         model = Category
#         lookup_field = 'slug'


# class GenreSerializer(serializers.ModelSerializer):

#     class Meta:
#         fields = ('name', 'slug')
#         model = Genre
#         lookup_field = 'slug'


# class TitleReadSerializer(serializers.ModelSerializer):
#     category = CategorySerializer(read_only=True)
#     genre = GenreSerializer(
#         read_only=True,
#         many=True
#     )
#     rating = serializers.IntegerField(read_only=True)

#     class Meta:
#         fields = ('id', 'name', 'year', 'description',
#                   'genre', 'category', 'rating',)
#         model = Title


# class TitleWriteSerializer(serializers.ModelSerializer):
#     category = serializers.SlugRelatedField(
#         queryset=Category.objects.all(),
#         slug_field='slug'
#     )
#     genre = serializers.SlugRelatedField(
#         queryset=Genre.objects.all(),
#         slug_field='slug',
#         many=True
#     )

#     class Meta:
#         fields = ('id', 'name', 'year', 'description',
#                   'genre', 'category')
#         model = Title


# class ReviewSerializer(serializers.ModelSerializer):

#     title = serializers.SlugRelatedField(
#         slug_field='name',
#         read_only=True
#     )

#     author = serializers.SlugRelatedField(
#         slug_field='username',
#         read_only=True,
#         default=serializers.CurrentUserDefault()
#     )

#     def validate_score(self, value):
#         if value < 0 or value > 10:
#             raise serializers.ValidationError(
#                 'Оценка должна быть целым числом(от 1 до 10)'
#             )
#         return value

#     def validate(self, data):
#         request = self.context['request']
#         author = request.user
#         title_id = self.context.get('view').kwargs.get('title_id')
#         title = get_object_or_404(Title, pk=title_id)
#         if (
#             request.method == 'POST'
#             and Review.objects.filter(title=title, author=author).exists()
#         ):
#             raise ValidationError('Можно оставить только один отзыв')
#         return data

#     class Meta:
#         fields = '__all__'
#         model = Review


# class CommentSerializer(serializers.ModelSerializer):
#     review = serializers.SlugRelatedField(
#         slug_field='text',
#         read_only=True
#     )
#     author = serializers.SlugRelatedField(
#         slug_field='username',
#         read_only=True
#     )

#     class Meta:
#         fields = '__all__'
#         model = Comment
