from autoslug import AutoSlugField
from django.conf import settings
from django.db import models
from django.utils.text import slugify
from unidecode import unidecode
from users.models import CustomUser


class Ingredient(models.Model):
    name = models.CharField(
        max_length=250,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=100
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ['name']

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name='Имя'
    )
    color = models.CharField(
        max_length=16,
        verbose_name='Цвет'
    )
    slug = AutoSlugField(
        unique=True,
        populate_from='name',
        verbose_name='Слаг'
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            transliterated_name = unidecode(self.name)
            self.slug = slugify(transliterated_name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ['name']

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=250)
    text = models.TextField(verbose_name='Описание рецепта')
    image = models.ImageField(
        upload_to='recipes/images/',
        null=True,
        default=None,
        verbose_name='Фото'
    )
    date = models.DateField(
        verbose_name='Дата создания',
        auto_now_add=True
    )
    cooking_time = (
        models.PositiveIntegerField(
            verbose_name='Время приготовления мин.')
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        related_name='recipes',
        verbose_name='Ингридиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тэги'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['author', 'date']

    def __str__(self):
        return self.text

    def is_favorited(self, user):
        return self.favorites.filter(user=user).exists()

    def is_in_shopping_cart(self, user):
        return self.shopping_carts.filter(user=user).exists()


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    amount = models.CharField(max_length=50)


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorite_recipes',
        verbose_name='Автор'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепты'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='shopping_cart_recipes',
        verbose_name='Автор'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепты'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
