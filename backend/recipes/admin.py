from django.contrib import admin

from recipes.models import Recipes, Ingridients


class IngridientsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'title', 'description',
                    'date', 'cooking_time', 'ingridients')
    empty_value_display = '-пусто-'
    list_editable = ('name', 'year', 'category')


admin.site.register(Recipes)
admin.site.register(Ingridients)
admin.site.register(IngridientsAdmin)
