from django.contrib.auth.models import AbstractUser
from django.db import models
from foodgram.settings import SLICE_OF_TEXT, SLICE_OF_TEXT_LONG

from .validators import validate_username


class User(AbstractUser):
    email = models.EmailField(
        max_length=254,
        unique=True,
        blank=False,
        null=False,
        verbose_name="Email",
        help_text="Email info",
    )
    username = models.CharField(
        validators=(validate_username,),
        max_length=150,
        unique=True,
        blank=False,
        null=False,
        verbose_name="Unique username",
        help_text="Username info",
    )
    first_name = models.CharField(
        max_length=150,
        blank=False,
        null=False,
        verbose_name="First name",
        help_text="First name info",
    )
    last_name = models.CharField(
        max_length=150,
        blank=False,
        null=False,
        verbose_name="Last name",
        help_text="Last name info",
    )

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=["email", "username"], name="unique_user"
            ),
        ]

    def __str__(self):
        return self.username[:SLICE_OF_TEXT]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name="follower",
        on_delete=models.CASCADE,
        verbose_name="Follower",
        help_text="Follower info",
    )
    author = models.ForeignKey(
        User,
        related_name="following",
        on_delete=models.CASCADE,
        verbose_name="Author",
        help_text="Author info",
    )

    class Meta:
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"

        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"],
                name="unique_follow",
            ),
            models.CheckConstraint(
                name="check_self_follow",
                check=~models.Q(user=models.F("author")),
            ),
        ]

    def __str__(self):
        return f"{self.user} follows {self.author}"[:SLICE_OF_TEXT_LONG]
