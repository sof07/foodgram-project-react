from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        USER = 'user', 'Пользователь'
        GUEST = 'guest', 'Гость'
        ADMIN = 'admin', 'Администратор'

    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(max_length=254)
    role = models.CharField(
        max_length=16, choices=Role.choices, default=Role.USER
    )
    confirmation_code = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('username', 'email', ),
                name='user'
            )]

    @property
    def is_user(self):
        return self.role == self.Role.USER

    @property
    def is_guest(self):
        return self.role == self.Role.GUEST  # Use Role.ADMIN instead of Role.MODERATOR

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    def save(self, *args, **kwargs):
        if self.username == 'me':
            pass
        super().save(*args, **kwargs)


class AuthorSubscription(models.Model):
    subscriber = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscribers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('subscriber', 'author')

    def __str__(self):
        return f"{self.subscriber} -> {self.author}"
