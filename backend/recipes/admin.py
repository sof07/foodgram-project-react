from django.contrib import admin
from .models import (Tag,
                     Ingredient,
                     Recipe,
                     IngredientRecipe,
                     Favorite,
                     ShoppingCart
                     )


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
    list_display = ('name', 'author', 'cooking_time', 'get_favorite_count')
    list_filter = ('author', 'tags', 'ingredients')
    search_fields = ('name', 'author__username')

    def get_favorite_count(self, obj):
        # Здесь вы можете написать код для получения общего числа добавления
        # рецепта в избранное для конкретного рецепта (obj).
        # Например, если у вас есть связь FavoriteRecipe с полем "recipe",
        # то вы можете использовать что-то вроде:
        return Favorite.objects.filter(recipe=obj).count()

    get_favorite_count.short_description = 'Добавлено в избранное'

    inlines = [IngredientRecipeInline]
