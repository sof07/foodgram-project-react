
from django_filters.rest_framework import (BooleanFilter, CharFilter,
                                           FilterSet,
                                           ModelMultipleChoiceFilter)

from .models import Recipe, Tag


class RecipeFilter(FilterSet):
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    author = CharFilter(
        field_name="author__id"
    )

    is_favorited = BooleanFilter(
        method='filter_is_favorited'
    )

    is_in_shopping_cart = BooleanFilter(
        method='filter_is_in_shopping_cart'
    )
    ingredients = CharFilter(
        field_name='ingredients__name',
        lookup_expr='icontains',
    )

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value:
            return queryset.filter(favorites__user=user)
        return queryset.exclude(favorites__user=user)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value:
            return queryset.filter(shopping_cart__user=user)
        return queryset.exclude(shopping_cart__user=user)

    class Meta:
        model = Recipe
        fields = ['tags', 'is_favorited',
                  'is_in_shopping_cart', 'author', 'ingredients']
