# Generated by Django 4.2.5 on 2023-09-11 17:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_follow_user_unique_user_follow_author_follow_user_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_subscribed',
            field=models.BooleanField(default=False, help_text='Информация подписан ли пользователь на автора', verbose_name='Подписка на автора'),
        ),
    ]