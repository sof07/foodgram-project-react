from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_reserved_username


class CustomUser(AbstractUser):
    email = models.EmailField(('email address'), unique=True, blank=False)
    first_name = models.CharField(('first name'), max_length=150, blank=False)
    last_name = models.CharField(('last name'), max_length=150, blank=False)
    username = models.CharField(
        ('username'),
        max_length=150,
        unique=True,
        validators=[validate_reserved_username]
    )
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
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'subscriber'),
                name='AuthorSubscription'
            )]

    def __str__(self):
        return f"{self.subscriber} -> {self.author}"
