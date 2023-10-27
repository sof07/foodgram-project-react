from django.contrib import admin
from django.forms import ModelForm

from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, Tag)

admin.site.empty_value_display = 'Не задано'


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


class PostForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ingredient'].required = True

    class Meta:
        model = IngredientRecipe
        fields = ('ingredient', 'amount')


class IngredientRecipeInline(admin.TabularInline):
    form = PostForm
    model = IngredientRecipe
    extra = 3
    # min_num = 1
    autocomplete_fields = ('ingredient',)
    # can_delete = False


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
