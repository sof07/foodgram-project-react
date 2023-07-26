from django.db import models
from users.models import User


class Ingredient(models.Model):
    title = models.CharField('Название ингредиента', max_length=250)
    quantity = models.DecimalField(
        'Количество', max_digits=10, decimal_places=2)
    unit_measurement = models.CharField('Единица измерения', max_length=100)


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes')
    title = models.CharField('Название рецепта', max_length=250)
    description = models.TextField('Описание рецепта')
    image = models.ImageField(
        upload_to='recipes/images/', null=True, default=None)
    date = models.DateField('Дата создания', auto_now_add=True)
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления мин.')
    ingredients = models.ManyToManyField(Ingredient, related_name='recipes')
    # tag =  # Commented out for now as it's not implemented yet
