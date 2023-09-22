from rest_framework import (filters, permissions, viewsets)
from collections import defaultdict
from .models import Recipe, Ingredient, Tag, ShoppingCart, Favorite
from users.models import AuthorSubscription, CustomUser
from .serializers import (IngredientSerializer,
                          TagSerializer,
                          RecipeCreateSerializer,
                          FavoriteRecipeSerializer,
                          RecipeFavoriteSerializer,
                          CustomUserSerializer,
                          SubscribeUserSerializer
                          )
from rest_framework.decorators import action
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.conf import settings
import csv
from rest_framework.pagination import LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from django.http import FileResponse
import os


class IngredientViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter, )
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeCreateSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ('name', 'tags')
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)  # Фильтрация
    filterset_fields = (
        'author',
        'tags')  # Поля для фильтрации

    @action(detail=False, methods=['get'], url_path='download_shopping_cart')
    def download_shopping_cart(self, request):

        shopping_cart_entries = ShoppingCart.objects.filter(user=request.user)
        # Создал словарь
        ingredient_totals = defaultdict(float)
        # Для каждого элемента в списке покупок получаю рецепты
        for entry in shopping_cart_entries:
            recipe = entry.recipe
            print(recipe)

            recipe_ingredients = recipe.recipe_ingredients.all()

            for ingredient_entry in recipe_ingredients:
                # Для каждого рецепта получаю ингридиен
                ingredient = ingredient_entry.ingredient
                amount_per_serving = ingredient_entry.amount
                total_amount = float(amount_per_serving)
                ingredient_totals[ingredient] += total_amount

        file_name = 'ingredients_list.csv'
        with open(file_name, 'w', newline='') as file:
            writer = csv.writer(file)
            for ingredient, total_amount in ingredient_totals.items():
                writer.writerow(
                    [f'{ingredient.name.capitalize()}, {total_amount}, {ingredient.measurement_unit}'])
        response = FileResponse(open(file_name, 'rb'), as_attachment=True)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        os.remove(file_name)
        return response

    @action(detail=True, methods=['post', 'delete'], url_path='shopping_cart')
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        user = request.user
        if request.method == 'POST':

            # Проверяем, существует ли уже запись об избранном для этого рецепта
            if not Favorite.objects.filter(user=user, recipe=recipe).exists():
                Favorite.objects.create(user=user, recipe=recipe)
                response_serializer = RecipeFavoriteSerializer(recipe)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {
                        'errors': 'Рецепт уже в избранном'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        elif request.method == 'DELETE':
            Favorite.objects.filter(user=user, recipe=recipe).delete()
            return Response()
    # Переопределение get_queryset для учёта авторства и состояния избранного/корзины

    # def get_queryset(self):
    #     queryset = Recipe.objects.all()
    #     user = self.request.user
    #     if user.is_authenticated:
    #         queryset = queryset.annotate_is_favorited(
    #             user).annotate_is_in_shopping_cart(user)
    #     return queryset

    # Переопределение create для обработки POST-запроса
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class TagViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class CustomUserViewSet(UserViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe')
    def subscribe(self, request, pk=None):
        user_to_subscribe = self.get_object()
        subscriber = self.request.user
        if request.method == 'POST':
            if user_to_subscribe == subscriber:
                return Response({"detail": "Вы не можете подписаться на себя."}, status=status.HTTP_400_BAD_REQUEST)
            subscription, created = AuthorSubscription.objects.get_or_create(
                subscriber=subscriber, author=user_to_subscribe)
            if created:
                response_serializer = SubscribeUserSerializer(
                    user_to_subscribe, context={'request': request})
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({"detail": "Вы уже подписаны на этого пользователя."}, status=status.HTTP_200_OK)
        elif request.method == 'DELETE':
            user_to_unsubscribe = self.get_object()
            subscriber = self.request.user
            try:
                subscription = AuthorSubscription.objects.get(
                    subscriber=subscriber, author=user_to_unsubscribe)
                subscription.delete()
                return Response({"detail": "Вы успешно отписались от этого пользователя."}, status=status.HTTP_204_NO_CONTENT)
            except AuthorSubscription.DoesNotExist:
                return Response({"detail":
                                 "Вы не были подписаны на этого пользователя."}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='subscriptions')
    def subscriptions(self, request):
        user = self.request.user  # Получаем текущего пользователя
        # здесь по релайтед наме получаем всех подписчиков
        subscribers = user.subscribers.all()
        response_serializer = SubscribeUserSerializer(
            subscribers, many=True, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def get_queryset(self):
        # Возвращаем все объекты CustomUser
        return CustomUser.objects.all()


class FavoriteViewset(viewsets.ModelViewSet):
    # queryset = Recipe.objects.all()
    queryset = Favorite.objects.all()
    serializer_class = FavoriteRecipeSerializer
