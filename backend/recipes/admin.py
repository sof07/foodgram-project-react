from django.contrib import admin

from recipes.models import Recipe, Ingredient


# class IngridientsAdmin(admin.ModelAdmin):
#     list_display = ('pk', 'author', 'title', 'description',
#                     'date', 'cooking_time', 'ingridients')
#     empty_value_display = '-пусто-'
#     list_editable = ('pk', 'author', 'title', 'description',
#                      'cooking_time', 'ingridients')


admin.site.register(Recipe)
admin.site.register(Ingredient)
# admin.site.register(IngridientsAdmin)
