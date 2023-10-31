from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class User(AbstractUser):
    email = models.EmailField('Электронная почта', max_length=254)
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)

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
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'follower'],
                name='unique_subscription'
            )
        ]

    def clean(self):
        if self.author == self.follower:
            raise ValidationError(
                {'author': 'Поле author не может равняться полю follower',
                 'follower': 'Поле follower не может равняться полю author'}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'A:{self.author} F:{self.follower}'
