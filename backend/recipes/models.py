from django.db import models
from users.models import CustomUser

from autoslug import AutoSlugField


class Ingredient(models.Model):
    """
    Ингредиент

    Атрибуты:
        title (str): Название ингредиента
        quantity (Decimal): Количество ингредиента
        unit_measurement (str): Единица измерения
    Методы:
        __str__(): Возвращает название ингредиента в виде строки
    """

    name = models.CharField(max_length=250)
    # amount = models.DecimalField(
    #     'Количество', max_digits=10, decimal_places=2)
    measurement_unit = models.CharField('Единица измерения', max_length=100)

    def __str__(self):
        return self.name


class Tag(models.Model):
    """
    Тег
    Атрибуты:
        name (str): Название тега
    Методы:
        __str__(): Возвращает название тега в виде строки
    """

    name = models.CharField(max_length=50)
    color = models.CharField(max_length=16)
    slug = AutoSlugField(unique=True, populate_from='name')

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """
    Рецепт

    Атрибуты:
        author (ForeignKey): Автор рецепта (связь с моделью User)
        title (str): Название рецепта
        description (str): Описание рецепта
        image (ImageField): Изображение рецепта
        date (DateField): Дата создания рецепта (автоматически заполняется при создании)
        cooking_time (PositiveIntegerField): Время приготовления в минутах
        ingredients (ManyToManyField): Ингредиенты рецепта (связь с моделью Ingredient через промежуточную модель IngredientRecipe)
        tag (ManyToManyField): Теги рецепта (связь с моделью Tag)

    """

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
        Ingredient, through='IngredientRecipe', related_name='ingredient')
    tags = models.ManyToManyField(Tag)

    def is_favorited(self, user):
        return self.favorites.filter(user=user).exists()

    def is_in_shopping_cart(self, user):
        return self.shopping_carts.filter(user=user).exists()


class IngredientRecipe(models.Model):
    """
    Промежуточная модель для связи ингредиентов с рецептом
    Атрибуты:
        Ingredient (ForeignKey): Ингредиент (связь с моделью Ingredient)
        recipe (ForeignKey): Рецепт (связь с моделью Recipe)
    """
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    amount = models.CharField(max_length=50)
