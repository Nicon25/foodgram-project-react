from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from foodgram.settings import SLICE_OF_TEXT, SLICE_OF_TEXT_LONG

from .validators import validate_slug

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="Tag name",
        help_text="Tag info",
    )
    color = models.CharField(
        max_length=7,
        null=True,
        verbose_name="Color in HEX",
        help_text="Tag color info",
    )
    slug = models.SlugField(
        validators=(validate_slug,),
        max_length=200,
        unique=True,
        verbose_name="Unique slug",
        help_text="Tag slug info",
    )

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=["slug"],
                name="unique_slug",
            ),
        ]

    def __str__(self):
        return self.name[:SLICE_OF_TEXT]


class Recipe(models.Model):
    ingredients = models.ManyToManyField(
        "Ingredient",
        through="IngredientInRecipe",
        related_name="recipe",
        verbose_name="List of ingredients",
        help_text="Ingredients info",
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="recipe",
        verbose_name="Tag IDs list",
        help_text="Tags info",
    )
    image = models.ImageField(
        upload_to="recipes/images/",
        verbose_name="Image encoded in Base64",
        help_text="Recipe image",
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Recipe name",
        help_text="Recipe info",
    )
    text = models.TextField(
        verbose_name="Description",
        help_text="Recipe description info",
    )
    cooking_time = models.IntegerField(
        validators=(MinValueValidator(1),),
        verbose_name="Preparation time in minutes.",
        help_text="Preparation time in minutes info",
    )
    author = models.ForeignKey(
        User,
        related_name="recipe",
        on_delete=models.CASCADE,
        verbose_name="Author",
        help_text="Author info",
    )

    class Meta:
        verbose_name = "Recipe"
        verbose_name_plural = "Recipes"
        ordering = ('-id',)

    def __str__(self):
        return self.name[:SLICE_OF_TEXT_LONG]


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Ingredient name",
        help_text="Ingredient info",
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name="Units of measurement",
        help_text="Units of measurement info",
    )

    class Meta:
        verbose_name = "Ingredient"
        verbose_name_plural = "Ingredients"

    def __str__(self):
        return f"{self.name} ({self.measurement_unit})"[:SLICE_OF_TEXT_LONG]


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_used",
        verbose_name="Recipe name",
        help_text="Recipe info",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="ingredient_used",
        verbose_name="Ingredient name",
        help_text="Ingredient name info",
    )
    amount = models.IntegerField(
        validators=(MinValueValidator(1),),
        verbose_name="Amount of the ingredient",
        help_text="Amount of the ingredient info",
    )

    class Meta:
        verbose_name = "Ingredient used in the recipe"
        verbose_name_plural = "Ingredients used in the recipe"
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"],
                name="unique_ingredient_in_recipe"
            )
        ]

    def __str__(self):
        return f"{self.ingredient} in {self.recipe}"[:SLICE_OF_TEXT_LONG]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="is_in_shopping_cart",
        verbose_name="User",
        help_text="User info",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="is_in_shopping_cart",
        verbose_name="Recipe name",
        help_text="Recipe info",
    )

    class Meta:
        verbose_name = "Recipe added to the shopping list"
        verbose_name_plural = "Recipes added to the shopping list"
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_recipe_in_shopping_cart"
            ),
        ]

    def __str__(self):
        return (
            f"'{self.recipe}' in the shopping list for '"
            f"{self.user}'"[:SLICE_OF_TEXT_LONG]
        )


class Favorites(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="is_favorited",
        verbose_name="User",
        help_text="User info",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="is_favorited",
        verbose_name="Recipe name",
        help_text="Recipe info",
    )

    class Meta:
        verbose_name = "Favorite recipe"
        verbose_name_plural = "Favorite recipes"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_recipe_in_favorites"
            ),
        ]

    def __str__(self):
        return (
            f"User '{self.user}' likes "
            f"{self.recipe}"[:SLICE_OF_TEXT_LONG]
        )
