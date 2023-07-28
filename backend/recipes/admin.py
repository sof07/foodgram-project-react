from django.contrib import admin

from recipes.models import Recipe, Ingredient, Tag, IngredientRecipe


class IngridientsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'title', 'description',
                    'date', 'cooking_time', 'ingridients', 'tag')


admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(Tag)
