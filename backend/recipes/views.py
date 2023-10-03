import csv
import os
from collections import defaultdict

from django.db.models import Q
from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from users.models import AuthorSubscription, CustomUser

from .filters import RecipeFilter
from .models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from .paginators import CustomPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (CustomUserSerializer, FavoriteRecipeSerializer,
                          IngredientSerializer, RecipeCreateSerializer,
                          RecipeFavoriteSerializer, SubscribeUserSerializer,
                          TagSerializer)


class IngredientViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter, )
    search_fields = ('^name',)

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        search_param = self.request.query_params.get('name')

        if search_param:
            queryset = queryset.filter(Q(name__istartswith=search_param))

        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeCreateSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (filters.OrderingFilter, DjangoFilterBackend)
    ordering_fields = ('date')
    pagination_class = CustomPagination
    filterset_class = RecipeFilter  # Поля для фильтрации

    @action(detail=False,
            methods=['get'],
            url_path='download_shopping_cart')
    def download_shopping_cart(self, request):

        shopping_cart_entries = ShoppingCart.objects.filter(user=request.user)
        ingredient_totals = defaultdict(float)
        for entry in shopping_cart_entries:
            recipe = entry.recipe
            recipe_ingredients = recipe.recipe_ingredients.all()

            for ingredient_entry in recipe_ingredients:
                ingredient = ingredient_entry.ingredient
                amount_per_serving = ingredient_entry.amount
                total_amount = float(amount_per_serving)
                ingredient_totals[ingredient] += total_amount

        file_name = 'ingredients_list.csv'
        with open(file_name, 'w', newline='') as file:
            writer = csv.writer(file)
            for ingredient, total_amount in ingredient_totals.items():
                writer.writerow(
                    [f'{ingredient.name.capitalize()}, {total_amount}, \
                     {ingredient.measurement_unit}']
                )
        response = FileResponse(open(file_name, 'rb'), as_attachment=True)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        os.remove(file_name)
        return response

    @action(detail=True,
            methods=['post', 'delete'],
            url_path='shopping_cart',)
    def shopping_cart(self, request, pk=None):
        try:
            recipe = Recipe.objects.get(pk=pk)

        except Recipe.DoesNotExist:
            return Response(
                {
                    'errors': 'Рецепт не существует'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user
        if request.method == 'POST':
            if user.is_authenticated:
                if not ShoppingCart.objects.filter(user=user, recipe=recipe).\
                        exists():
                    ShoppingCart.objects.create(user=user, recipe=recipe)
                    response_serializer = RecipeFavoriteSerializer(recipe)
                    return Response(
                        response_serializer.data,
                        status=status.HTTP_201_CREATED
                    )
                else:
                    return Response(
                        {
                            'errors': 'Запрос от анонимного пользователя'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            if user.is_authenticated:
                ShoppingCart.objects.filter(user=user, recipe=recipe).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            methods=['post', 'delete'],
            url_name='favorite',
            permission_classes=[permissions.IsAuthenticated]
            )
    def favorite(self, request, pk=None):
        try:
            recipe = Recipe.objects.get(pk=pk)

        except Recipe.DoesNotExist:
            return Response(
                {
                    'errors': 'Запрос от анонимного пользователя'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user
        if request.method == 'POST':

            print(self.get_object())
            if not Favorite.objects.filter(user=user, recipe=recipe).exists():
                Favorite.objects.create(user=user, recipe=recipe)
                response_serializer = RecipeFavoriteSerializer(recipe)
                return Response(
                    response_serializer.data,
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {
                        'errors': 'Рецепт уже в избранном'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        elif request.method == 'DELETE':
            Favorite.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class TagViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class CustomUserViewSet(UserViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    lookup_field = 'pk'
    permission_classes = [permissions.AllowAny]

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='subscribe',
        permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, pk=None):
        user_to_subscribe = self.get_object()
        subscriber = self.request.user
        if request.method == 'POST':
            if user_to_subscribe == subscriber:
                return Response(
                    {"detail": "Вы не можете подписаться на себя."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscription, created = AuthorSubscription.objects.get_or_create(
                subscriber=subscriber, author=user_to_subscribe)
            if created:
                response_serializer = SubscribeUserSerializer(
                    user_to_subscribe, context={'request': request})
                return Response(
                    response_serializer.data,
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {"detail": "Вы уже подписаны на этого пользователя."},
                    status=status.HTTP_403_FORBIDDEN
                )
        elif request.method == 'DELETE':
            user_to_unsubscribe = self.get_object()
            subscriber = self.request.user
            try:
                subscription = AuthorSubscription.objects.get(
                    subscriber=subscriber, author=user_to_unsubscribe)
                subscription.delete()
                return Response(
                    {"detail": "Вы успешно отписались от этого пользователя."},
                    status=status.HTTP_204_NO_CONTENT
                )
            except AuthorSubscription.DoesNotExist:
                return Response(
                    {"detail": "Вы не были подписаны на этого пользователя."},
                    status=status.HTTP_400_BAD_REQUEST
                )

    @action(detail=False,
            methods=['get'],
            url_path='subscriptions',
            permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request):
        user = self.request.user
        subscribed_authors = AuthorSubscription.objects.filter(
            subscriber=user).values('author')
        subscribed_users = CustomUser.objects.filter(pk__in=subscribed_authors)

        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(subscribed_users, request)

        response_serializer = SubscribeUserSerializer(
            result_page, many=True, context={'request': request})

        return paginator.get_paginated_response(response_serializer.data)


class FavoriteViewset(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteRecipeSerializer
