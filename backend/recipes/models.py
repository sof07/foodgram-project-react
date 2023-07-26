from django.db import models
from users.models import User

class Ingridients(models.Model):
    title = models.CharField('Название ингридиента', max_length=250)
    quantity = models.DecimalField('Количество', max_length=1000)
    unit_measurement = models.CharField('Единица измерения', max_length=100)

class Recipes(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes')
    title = models.CharField('Название рецепта', max_length=250)
    description = models.TextField('Описание рецепта')
    image = models.ImageField(
        upload_to='recipes/images/', 
        null=True,  
        default=None
        )
    date = models.DateField('Дата создания', auto_now_add=True)
    cooking_time = models.DecimalField('Время приготовления мин.' max_length=4) #Подумать над типом поля
    ingridients = models.ManyToManyField(
        Ingridients,
        related_name='recipes',
    )
    #tag =
