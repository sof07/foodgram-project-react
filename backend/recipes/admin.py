from django.contrib import admin

from recipes.models import Recipe, Ingredient, Tag

class IngridientsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'title', 'description',
                    'date', 'cooking_time', 'ingridients', 'tag')
    
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author','name', 'image', 'text', 'cooking_time')


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient)
admin.site.register(Tag)

