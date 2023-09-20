# Generated by Django 4.2.5 on 2023-09-14 14:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0004_remove_user_is_subscribed"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="is_subscribed",
            field=models.BooleanField(
                default=False,
                help_text="Информация подписан ли пользователь на автора",
                verbose_name="Подписка на автора",
            ),
        ),
    ]
