from django.contrib.auth.models import AbstractUser
from django.db import models

from foodgram.settings import SLICE_OF_TEXT, SLICE_OF_TEXT_LONG
from .validators import validate_username

# user взял из api_yamdb
ROLE_CHOICES = (
    ('user', 'Пользователь'),
    ('moderator', 'Модератор'),
    ('admin', 'Администратор'),
)

class User(AbstractUser):
    email = models.EmailField(
        max_length=254,
        unique=True,
        blank=False,
        null=False,
        verbose_name='Адрес электронной почты',
        help_text='Информация о адресе электронной почты',
    )
    username = models.CharField(
        validators=(validate_username,),
        max_length=150,
        unique=True,
        blank=False,
        null=False,
        verbose_name='Уникальный юзернейм',
        help_text='Информация о юзернейме',
    )
    first_name = models.CharField(
        max_length=150,
        blank=False,
        null=False,
        verbose_name='Имя',
        help_text='Информация о имени пользователя',
    )
    last_name = models.CharField(
        max_length=150,
        blank=False,
        null=False,
        verbose_name='Фамилия',
        help_text='Информация о фамилии пользователя',
    )
    password = models.CharField(
        max_length=150,
        blank=False,
        null=False,
        verbose_name='Пароль',
        help_text='Информация о пароле',
    )

    @property
    def is_user(self):
        return self.role == 'user'

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_moderator(self):
        return self.role == 'moderator'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=['email', 'username'],
                name='unique_user'
            ),
        ]

    def __str__(self):
        return self.username[:SLICE_OF_TEXT]


# follow взял из hw5_final
class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        help_text='Информация о подписчике',
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE,
        verbose_name='Автор',
        help_text='Информация об авторе',
    )

    class Meta:
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follow',
            ),
            models.CheckConstraint(
                name='check_self_follow',
                check=~models.Q(user=models.F('author')),
            ),
        ]

    def __str__(self):
        return f'{self.user} follows {self.author}'[:SLICE_OF_TEXT_LONG]