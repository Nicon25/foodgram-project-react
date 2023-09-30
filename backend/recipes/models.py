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
        verbose_name="Название",
        help_text="Информация о теге",
    )
    color = models.CharField(
        max_length=7,
        null=True,
        verbose_name="Цвет в HEX",
        help_text="Информация о цвете тега",
    )
    slug = models.SlugField(
        validators=(validate_slug,),
        max_length=200,
        unique=True,
        verbose_name="Уникальный слаг",
        help_text="Информация о слаге тега",
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ('-id')
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
        verbose_name="Список ингредиентов",
        help_text="Информация о ингредиентах",
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="recipe",
        verbose_name="Список id тегов",
        help_text="Информация о тегах",
    )
    image = models.ImageField(
        upload_to="recipes/images/",
        verbose_name="Картинка, закодированная в Base64",
        help_text="Картинка рецепта",
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Название",
        help_text="Название рецепта",
    )
    text = models.TextField(
        verbose_name="Описание",
        help_text="Описание рецепта",
    )
    cooking_time = models.IntegerField(
        validators=(MinValueValidator(1),),
        verbose_name="Время приготовления в минутах",
        help_text="Информация о времени приготовления рецепта",
    )
    author = models.ForeignKey(
        User,
        related_name="recipe",
        on_delete=models.CASCADE,
        verbose_name="Автор рецепта",
        help_text="Информация об авторе рецепта",
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ('-id')

    def __str__(self):
        return self.name[:SLICE_OF_TEXT_LONG]


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Название ингредиента",
        help_text="Информация о ингредиенте",
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name="Единицы измерения",
        help_text="Информация о единицах измерения ингредиента",
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return f"{self.name} ({self.measurement_unit})"[:SLICE_OF_TEXT_LONG]


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_used",
        verbose_name="Название рецепта",
        help_text="Информация о названии рецепта",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="ingredient_used",
        verbose_name="Название ингредиента",
        help_text="Информация о названии ингредиента",
    )
    amount = models.IntegerField(
        validators=(MinValueValidator(1),),
        verbose_name="Количество ингредиента",
        help_text="Информация о необходимом количестве ингредиента",
    )

    class Meta:
        verbose_name = "Ингредиент, используемый в рецепте"
        verbose_name_plural = "Ингредиенты, используемые в рецепте"
        ordering = ('-id')
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
        verbose_name="Пользователь",
        help_text="Информация о пользователе",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="is_in_shopping_cart",
        verbose_name="Название рецепта",
        help_text="Информация о названии рецепта",
    )

    class Meta:
        verbose_name = "Рецепт, добавленный в список покупок"
        verbose_name_plural = "Рецепты, добавленые в список покупок"
        ordering = ('-id')
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_recipe_in_shopping_cart"
            ),
        ]

    def __str__(self):
        return (
            f"'{self.recipe}' в списке покупок у '"
            f"{self.user}'"[:SLICE_OF_TEXT_LONG]
        )


class Favorites(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="is_favorited",
        verbose_name="Пользователь",
        help_text="Информация о пользователе",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="is_favorited",
        verbose_name="Название рецепта",
        help_text="Информация о названии рецепта",
    )

    class Meta:
        verbose_name = "Любимый рецепт"
        verbose_name_plural = "Любимые рецепты"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_recipe_in_favorites"
            ),
        ]

    def __str__(self):
        return (
            f"Пользователь '{self.user}' любит "
            f"{self.recipe}"[:SLICE_OF_TEXT_LONG]
        )
