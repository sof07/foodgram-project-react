from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, Tag)


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    extra = 1
    min_num = 1


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
                    'image', 'get_favorite_count',)
    list_filter = ('author', 'tags', 'ingredients',)
    search_fields = ('name', 'author__username',)
    filter_horizontal = ['tags']

    def get_favorite_count(self, obj):
        return Favorite.objects.filter(recipe=obj).count()

    get_favorite_count.short_description = 'Добавлено в избранное'

    inlines = [IngredientRecipeInline]
