import base64

from django.core.files.base import ContentFile
from django.db.models import F
from djoser.serializers import UserCreateSerializer
from recipes.models import (Favorites, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from users.models import Follow, User


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

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

    def get_is_subscribed(self, object):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user, author=object
        ).exists()


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
                "Тew password must be different from the old one."
            )
        return data


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("id", "name", "color", "slug")
        model = Tag


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
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

    def get_ingredients(self, object: Recipe):
        ingredients = object.ingredients.values(
            'id', 'name', 'measurement_unit',
            amount=F('ingredient_used__amount')
        )
        return ingredients

    def is_object_in_list(self, object, list_model):
        request = self.context.get('request')

        if request is None or request.user.is_anonymous:
            return False

        return list_model.objects.filter(
            user=request.user,
            recipe_id=object
        ).exists()

    def get_is_favorited(self, object):
        return self.is_object_in_list(object, Favorites)

    def get_is_in_shopping_cart(self, object):
        return self.is_object_in_list(object, ShoppingCart)


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
                'Add at least one ingredient'
            )

        for ingredient in ingredients:
            name = ingredient['id']
            if name in distinct_ingredients:
                raise serializers.ValidationError(
                    f'A repeated ingredient has been added to the recipe - {name}'
                )
            else:
                distinct_ingredients.append(name)
            if int(ingredient['amount']) <= 0:
                raise serializers.ValidationError(
                    f'An incorrect quantity of the ingredient is specified - {name}'
                )
        return data


class SubscriptionSerializer(serializers.ModelSerializer):
    recipes = SerializerMethodField(read_only=True)
    recipes_count = SerializerMethodField(read_only=True)
    is_subscribed = SerializerMethodField(read_only=True)

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
        recipe_limit = request.query_params.get("recipes_limit")
        queryset = Recipe.objects.filter(author=object)

        if recipe_limit:
            queryset = queryset[: int(recipe_limit)]
        return RecipeForSubscriptionSerializer(
            queryset, many=True, context=context
        ).data

    def get_recipes_count(self, object):
        return Recipe.objects.filter(author=object).count()

    def get_is_subscribed(self, object):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user, author=object
        ).exists()


class RecipeForSubscriptionSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        fields = ("id", "name", "image", "cooking_time")
        model = Recipe
