# Generated by Django 3.2.16 on 2023-09-27 18:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0007_auto_20230927_1828'),
    ]

    operations = [
        migrations.AlterField(
            model_name='favorites',
            name='recipe',
            field=models.ForeignKey(help_text='Информация о названии рецепта', on_delete=django.db.models.deletion.CASCADE, related_name='favorite', to='recipes.recipe', verbose_name='Название рецепта'),
        ),
        migrations.AlterField(
            model_name='favorites',
            name='user',
            field=models.ForeignKey(help_text='Информация о пользователе', on_delete=django.db.models.deletion.CASCADE, related_name='favorite', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
    ]
