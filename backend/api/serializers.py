import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer
from recipes.models import (Favorites, Ingredient, IngredientInRecipe, Recipe,
                            Tag)
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from users.models import Follow, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed"
        )
        model = User

    def create(self, validated_data):
        user = User(
            email=validated_data["email"], username=validated_data["username"]
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = (
            "id", "email", "username",
            "first_name", "last_name", "password"
        )


class ChangePasswordSerializer(serializers.Serializer):
    class Meta:
        fields = ("current_password", "new_password")

    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate(self, data):
        if data["current_password"] == data["new_password"]:
            raise serializers.ValidationError(
                "Новый пароль должен отличаться от старого."
            )
        return data


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Follow


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("id", "name", "color", "slug")
        model = Tag


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        # Если полученный объект строка, и эта строка
        # начинается с 'data:image'...
        if isinstance(data, str) and data.startswith("data:image"):
            # ...начинаем декодировать изображение из base64.
            # Сначала нужно разделить строку на части.
            format, imgstr = data.split(";base64,")
            # И извлечь расширение файла.
            ext = format.split("/")[-1]
            # Затем декодировать сами данные и поместить результат в файл,
            # которому дать название по шаблону.
            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)

        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)
    author = serializers.CharField(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        model = Recipe

    def get_is_favorited(self, object):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return object.is_favorited.filter(user=request.user).exists()
        return False

    def get_is_in_shopping_cart(self, object):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return object.is_in_shopping_cart.filter(
                user=request.user
            ).exists()
        return False


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Ingredient


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = IngredientInRecipe


class FavoritesSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Favorites


class RecipeForSubscriptionSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        fields = ("name", "image", "cooking_time")
        model = Recipe


class SubscriptionSerializer(serializers.ModelSerializer):
    recipes = SerializerMethodField(read_only=True)
    recipes_count = SerializerMethodField(read_only=True)

    class Meta:
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )
        model = User

    def get_recipes(self, object):
        request = self.context.get("request")
        context = {"request": request}
        recipe_limit = request.query_params.get("recipe_limit")
        queryset = Recipe.objects.filter(author=object)

        if recipe_limit:
            queryset = queryset[: int(recipe_limit)]
        return RecipeForSubscriptionSerializer(
            queryset, many=True, context=context
        ).data

    def get_recipes_count(self, object):
        return Recipe.objects.filter(author=object).count()
