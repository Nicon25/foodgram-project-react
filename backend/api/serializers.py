from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from users.models import User, Follow
from recipes.models import Tag, Recipe, Ingredient, IngredientInRecipe, ShoppingCart, Favorites

# взял из api_yambd
# class ObtainTokenSerializer(serializers.ModelSerializer):
#     username = serializers.CharField(max_length=50)
#     confirmation_code = serializers.CharField(max_length=15)

#     class Meta:
#         model = User
#         fields = ('username', 'confirmation_code')


# class RegistrationSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = User
#         fields = ('email', 'username')

#     def validate(self, data):
#         # Проверяем, есть ли уже пользователь с таким именем
#         username = data.get('username')
#         if User.objects.filter(username=username).exists():
#             raise serializers.ValidationError(
#                 'Пользователь с таким именем уже зарегистрирован'
#             )

#         # Проверяем, есть ли уже пользователь с таким email
#         email = data.get('email')
#         if User.objects.filter(email=email).exists():
#             raise serializers.ValidationError(
#                 'Пользователь с таким email уже зарегистрирован'
#             )

#         # Валидируем, что пользователь не будет использовать никнейм,
#         # конфликтующий с эндпоинтом
#         if username != 'me':
#             return data

#         raise serializers.ValidationError('Невозможное имя пользователя')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('__all__')
        model = User
    #     extra_kwargs = {'email': {'required': True},
    #                     'role': {'read_only': True},
    #                     'username': {'required': True}}

    # def validate(self, data):
    #     if data.get('username') != 'me':
    #         return data
    #     raise serializers.ValidationError(
    #         'Вы не можете дать такое имя'
    #     )

class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('__all__')
        model = Follow


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('__all__')
        model = Tag


class RecipeSerializer(serializers.ModelSerializer):
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


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('__all__')
        model = ShoppingCart


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
