from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, Tag)


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    extra = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'created_at')
    search_fields = ('user', 'recipe')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'cooking_time',
                    'get_html_photo', 'get_favorite_count')
    list_filter = ('author', 'tags', 'ingredients')
    search_fields = ('name', 'author__username')

    def get_html_photo(self, object):
        if object.image:
            return mark_safe(f"<img src='{object.image.url}'eidth=50")

    def get_favorite_count(self, obj):
        return Favorite.objects.filter(recipe=obj).count()

    get_favorite_count.short_description = 'Добавлено в избранное'
    get_html_photo.short_description = 'Изображение'

    inlines = [IngredientRecipeInline]
