from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        USER = 'user', 'Пользователь'
        ADMIN = 'admin', 'Администратор'

    role = models.CharField(
        max_length=16, choices=Role.choices, default=Role.USER
    )
    REQUIRED_FIELDS =['email','first_name', 'last_name']

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
        return self.role == self.Role.GUEST  

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    def save(self, *args, **kwargs):
        if self.username == 'me':
            pass
        super().save(*args, **kwargs)
    def has_subscriptions(self):
        return AuthorSubscription.objects.filter(subscriber=self).exists()


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
