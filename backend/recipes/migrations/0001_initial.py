# Generated by Django 4.2.5 on 2023-09-07 13:24

import django.core.validators
import django.db.models.deletion
import recipes.validators
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Favorites",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
            ],
            options={
                "verbose_name": "Любимый рецепт",
                "verbose_name_plural": "Любимые рецепты",
            },
        ),
        migrations.CreateModel(
            name="Ingredient",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Информация о ингредиенте",
                        max_length=200,
                        verbose_name="Название ингредиента",
                    ),
                ),
                (
                    "measurement_unit",
                    models.CharField(
                        help_text="Информация о единицах измерения ингредиента",
                        max_length=200,
                        verbose_name="Единицы измерения",
                    ),
                ),
            ],
            options={
                "verbose_name": "Ингредиент",
                "verbose_name_plural": "Ингредиенты",
            },
        ),
        migrations.CreateModel(
            name="IngredientInRecipe",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "amount",
                    models.IntegerField(
                        help_text="Информация о необходимом количестве ингредиента",
                        validators=[django.core.validators.MinValueValidator(1)],
                        verbose_name="Количество ингредиента",
                    ),
                ),
            ],
            options={
                "verbose_name": "Ингредиент, используемый в рецепте",
                "verbose_name_plural": "Ингредиенты, используемые в рецепте",
            },
        ),
        migrations.CreateModel(
            name="Recipe",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "image",
                    models.ImageField(
                        help_text="Картинка рецепта",
                        upload_to="recipes/images/",
                        verbose_name="Картинка, закодированная в Base64",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Название рецепта",
                        max_length=200,
                        verbose_name="Название",
                    ),
                ),
                (
                    "text",
                    models.TextField(
                        help_text="Описание рецепта", verbose_name="Описание"
                    ),
                ),
                (
                    "cooking_time",
                    models.IntegerField(
                        help_text="Информация о времени приготовления рецепта",
                        validators=[django.core.validators.MinValueValidator(1)],
                        verbose_name="Время приготовления в минутах",
                    ),
                ),
            ],
            options={
                "verbose_name": "Рецепт",
                "verbose_name_plural": "Рецепты",
            },
        ),
        migrations.CreateModel(
            name="ShoppingCart",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
            ],
            options={
                "verbose_name": "Рецепт добавлен в список покупок",
                "verbose_name_plural": "Рецепты добавлены в список покупок",
            },
        ),
        migrations.CreateModel(
            name="Tag",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Информация о теге",
                        max_length=200,
                        unique=True,
                        verbose_name="Название",
                    ),
                ),
                (
                    "color",
                    models.CharField(
                        help_text="Информация о цвете тега",
                        max_length=7,
                        null=True,
                        verbose_name="Цвет в HEX",
                    ),
                ),
                (
                    "slug",
                    models.SlugField(
                        help_text="Информация о слаге тега",
                        max_length=200,
                        unique=True,
                        validators=[recipes.validators.validate_slug],
                        verbose_name="Уникальный слаг",
                    ),
                ),
            ],
            options={
                "verbose_name": "Тег",
                "verbose_name_plural": "Теги",
            },
        ),
        migrations.AddConstraint(
            model_name="tag",
            constraint=models.UniqueConstraint(fields=("slug",), name="unique_slug"),
        ),
        migrations.AddField(
            model_name="shoppingcart",
            name="recipe",
            field=models.ForeignKey(
                help_text="Информация о названии рецепта",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="is_in_shopping_cart",
                to="recipes.recipe",
                verbose_name="Название рецепта",
            ),
        ),
        migrations.AddField(
            model_name="shoppingcart",
            name="user",
            field=models.ForeignKey(
                help_text="Информация о пользователе",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="is_in_shopping_cart",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Пользователь",
            ),
        ),
        migrations.AddField(
            model_name="recipe",
            name="author",
            field=models.ForeignKey(
                help_text="Информация об авторе рецепта",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="recipe",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Автор рецепта",
            ),
        ),
        migrations.AddField(
            model_name="recipe",
            name="ingredients",
            field=models.ManyToManyField(
                help_text="Информация о ингредиентах",
                related_name="recipe",
                through="recipes.IngredientInRecipe",
                to="recipes.ingredient",
                verbose_name="Список ингредиентов",
            ),
        ),
        migrations.AddField(
            model_name="recipe",
            name="tags",
            field=models.ManyToManyField(
                help_text="Информация о тегах",
                related_name="recipe",
                to="recipes.tag",
                verbose_name="Список id тегов",
            ),
        ),
        migrations.AddField(
            model_name="ingredientinrecipe",
            name="ingredient",
            field=models.ForeignKey(
                help_text="Информация о названии ингредиента",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="ingredient_used",
                to="recipes.ingredient",
                verbose_name="Название ингредиента",
            ),
        ),
        migrations.AddField(
            model_name="ingredientinrecipe",
            name="recipe",
            field=models.ForeignKey(
                help_text="Информация о названии рецепта",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="recipe_used",
                to="recipes.recipe",
                verbose_name="Название рецепта",
            ),
        ),
        migrations.AddField(
            model_name="favorites",
            name="recipe",
            field=models.ForeignKey(
                help_text="Информация о названии рецепта",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="is_favorited",
                to="recipes.recipe",
                verbose_name="Название рецепта",
            ),
        ),
        migrations.AddField(
            model_name="favorites",
            name="user",
            field=models.ForeignKey(
                help_text="Информация о пользователе",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="is_favorited",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Пользователь",
            ),
        ),
        migrations.AddConstraint(
            model_name="ingredientinrecipe",
            constraint=models.UniqueConstraint(
                fields=("recipe", "ingredient"), name="unique_ingredient_in_recipe"
            ),
        ),
        migrations.AddConstraint(
            model_name="favorites",
            constraint=models.UniqueConstraint(
                fields=("user", "recipe"), name="unique_recipe_in_favorites"
            ),
        ),
    ]
