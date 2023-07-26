from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        USER = 'user', 'Пользователь'
        GUEST = 'guest', 'Гсть'
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
    def is_moderator(self):
        return self.role == self.Role.MODERATOR

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    def save(self, *args, **kwargs):
        if self.username == 'me':
            pass
        super().save(*args, **kwargs)
