from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        'Электронная почта',
        max_length=254,
        unique=True
    )
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)

    class Meta:
        ordering = ('id',)

    def __str__(self) -> str:
        return self.username


class Subscription(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following_authors',
    )
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
    )

    class Meta:
        ordering = ('id',)
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'follower'],
                name='unique_subscription'
            ),
            models.CheckConstraint(
                check=~models.Q(follower=models.F('author')),
                name='forbidden_self_subscription'
            )
        ]

    def __str__(self) -> str:
        return f'A:{self.author} F:{self.follower}'
