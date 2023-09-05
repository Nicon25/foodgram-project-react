from django.db import models
from foodgram.settings import SLICE_OF_TEXT


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