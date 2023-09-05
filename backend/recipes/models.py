from django.core.validators import MinValueValidator
from django.db import models
from users.models import User


from foodgram.settings import SLICE_OF_TEXT
from validators import validate_slug


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
        unique=True
    )
    color = models.CharField(
        max_length=7,
        verbose_name='Цвет в HEX',
        null = True
    )
    slug = models.SlugField(
        validators=(validate_slug,),
        max_length=200,
        verbose_name='Уникальный слаг',
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        constraints = [
            models.UniqueConstraint(
                fields=['slug'],
                name='unique_slug',
            ),
        ]

    def __str__(self):
        return self.name[:SLICE_OF_TEXT]


class Recipe(models.Model):
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='RecipeIngredient',
        related_name='recipe',
        verbose_name='Список ингредиентов',
        help_text='Информация о ингредиентах',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Список id тегов',
        help_text='Информация о тегах',
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Картинка, закодированная в Base64',
        help_text='Картинка рецепта',
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Название рецепта',
    )
    text = models.TextField(
        verbose_name='Описание',
        help_text='Описание рецепта',
    )
    cooking_time = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Время приготовления в минутах',
        help_text='Информация о времени приготовления рецепта',
    )
    author = models.ForeignKey(
        User,
        related_name='recipes',
        verbose_name='Автор рецепта',
        help_text='Информация об авторе рецепта',
         #on_delete=models.CASCADE,   #не уверен что нужно удалять - подумать можно ли оставить рецепты как ноунейм при удалении юзера
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name[:SLICE_OF_TEXT]