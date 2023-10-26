from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, Tag)

admin.site.empty_value_display = 'Не задано'


class IngredientRecipeForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ingredient'].required = True

    class Meta:
        model = IngredientRecipe
        fields = ('ingredient', 'recipe', 'amount')


class IngredientRecipeInline(admin.TabularInline):
    form = IngredientRecipeForm
    model = IngredientRecipe
    extra = 1
    # min_num = 1


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


class IngredientRecipeForm(ModelForm):
    class Meta:
        model = IngredientRecipe
        fields = ('ingredient', 'recipe', 'amount')

    def clean(self):
        cleaned_data = super().clean()
        ingredients = cleaned_data.get('ingredient')

        if not ingredients:
            raise ValidationError('At least one ingredient is required.')


class IngredientRecipeInline(admin.TabularInline):
    form = IngredientRecipeForm
    model = IngredientRecipe
    extra = 0  # Set extra to 0
    min_num = 1  # Set min_num to 1


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
