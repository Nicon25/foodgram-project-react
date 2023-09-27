import base64

from django.core.files.base import ContentFile
from django.db.models import F
from djoser.serializers import UserCreateSerializer
from recipes.models import (Favorites, Ingredient, IngredientInRecipe, Recipe,
                            Tag)
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from users.models import User


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


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    ingredients = serializers.SerializerMethodField()

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

    def get_ingredients(self, obj: Recipe):
        ingredients = obj.ingredients.values(
            'id', 'name', 'measurement_unit',
            amount=F('ingredient_used__amount')
        )
        return ingredients

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


class RecipeCreateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = IngredientInRecipeSerializer(many=True)
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'name',
            'ingredients',
            'image',
            'text',
            'cooking_time'
        )

    def ingredients_in_recipe(self, ingredients, recipe):
        for ingredient in ingredients:
            ingredient_name = ingredient['id']
            ingredient_amount = ingredient['amount']
            ingredients, created = IngredientInRecipe.objects.get_or_create(
                recipe=recipe,
                ingredient=ingredient_name,
                amount=ingredient_amount
            )

    def to_representation(self, instance):
        serializer = RecipeSerializer(instance)
        return serializer.data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        recipe.save()
        self.ingredients_in_recipe(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.ingredients.clear()
        self.ingredients_in_recipe(ingredients, instance)
        instance.tags.set(tags)
        instance.save()
        return instance

    def validate(self, data):
        ingredients = data['ingredients']
        distinct_ingredients = []

        if len(ingredients) < 1:
            raise serializers.ValidationError(
                'Добавьте хотя бы один ингредиент'
            )

        for ingredient in ingredients:
            name = ingredient['id']
            if name in distinct_ingredients:
                raise serializers.ValidationError(
                    f'В рецепт добавлен повторяющийся ингредиент - {name}'
                )
            else:
                distinct_ingredients.append(name)
            if int(ingredient['amount']) <= 0:
                raise serializers.ValidationError(
                    f'Указано не корректное количество ингредиента - {name}'
                )
        return data


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
        recipe_limit = request.query_params.get("recipe_limit")

        if recipe_limit:
            RecipeForSubscriptionSerializer(
                object.recipes.all()[:int(recipe_limit)], many=True,
            ).data


    def get_recipes_count(self, object):
        return Recipe.objects.filter(author=object).count()

    def get_is_subscribed(self, obj: User):
        return True


class RecipeForSubscriptionSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        fields = ("id", "name", "image", "cooking_time")
        model = Recipe


class FavoritesSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Favorites
