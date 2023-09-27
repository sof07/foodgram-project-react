from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class CustomUser(AbstractUser):
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('username', 'email',),
                name='user'
            )]
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['email', 'username']


class AuthorSubscription(models.Model):
    subscriber = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscribers'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания')

    class Meta:
        unique_together = ('subscriber', 'author')

    def __str__(self):
        return f"{self.subscriber} -> {self.author}"
