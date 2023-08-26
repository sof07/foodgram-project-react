from django.db import models
from users.models import CustomUser
from django.conf import settings
from autoslug import AutoSlugField


class Ingredient(models.Model):
    name = models.CharField(max_length=250)
    measurement_unit = models.CharField('Единица измерения', max_length=100)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=16)
    slug = AutoSlugField(unique=True, populate_from='name')

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='recipes')
    name = models.CharField('Название рецепта', max_length=250)
    text = models.TextField('Описание рецепта')
    image = models.ImageField(
        upload_to='recipes/images/', null=True, default=None)
    date = models.DateField('Дата создания', auto_now_add=True)
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления мин.')
    ingredients = models.ManyToManyField(
        Ingredient, through='IngredientRecipe', related_name='recipes')
    tags = models.ManyToManyField(Tag, related_name='recipes')

    def __str__(self):
        return self.text

    def is_favorited(self, user):
        return self.favorites.filter(user=user).exists()

    def is_in_shopping_cart(self, user):
        return self.shopping_carts.filter(user=user).exists()


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name='recipe_ingredients')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    amount = models.CharField(max_length=50)


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='favorite_recipes'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='favorites'
    )
    created_at = models.DateTimeField(auto_now_add=True)


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='shopping_cart_recipes'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='shopping_cart'
    )
    created_at = models.DateTimeField(auto_now_add=True)
