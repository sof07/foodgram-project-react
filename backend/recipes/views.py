from rest_framework import (filters, permissions, viewsets)

from .models import Recipe, Ingredient, Tag, ShoppingCart, Favorite
from users.models import AuthorSubscription
from .serializers import (RecipeSerializer,
                          IngredientSerializer,
                          TagSerializer,
                          AuthorSubscriptionSerialaser,
                          RecipeCreateSerializer
                          )
from rest_framework.decorators import action
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import status

from django.conf import settings


class IngredientViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    search_fields = ('name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ('name', 'cooking_time')

    @action(detail=True, methods=['post'])
    def shopping_cart(self, request, pk=None):
        try:
            recipe = Recipe.objects.get(pk=pk)
        except Recipe.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        user = request.user
        shopping_cart_item, created = ShoppingCart.objects.get_or_create(
            user=user, recipe=recipe
        )

        if created:
            return Response({
                'id': recipe.id,
                'name': recipe.name,
                'image': recipe.image.url,
                'cooking_time': recipe.cooking_time
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        user = request.user

        # Проверяем, существует ли уже запись об избранном для этого рецепта
        if not Favorite.objects.filter(user=user, recipe=recipe).exists():
            Favorite.objects.create(user=user, recipe=recipe)
            response_serializer = RecipeSerializer(recipe)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    # Переопределение get_queryset для учёта авторства и состояния избранного/корзины
    # def get_queryset(self):
    #     queryset = Recipe.objects.all()
    #     user = self.request.user
    #     if user.is_authenticated:
    #         queryset = queryset.annotate_is_favorited(
    #             user).annotate_is_in_shopping_cart(user)
    #     return queryset

    # Переопределение create для обработки POST-запроса
    def create(self, request, *args, **kwargs):
        serializer = RecipeCreateSerializer(data=request.data)
        print(serializer)
        if serializer.is_valid():
            # Передача текущего авторизованного пользователя
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        serializer = RecipeCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Передача текущего авторизованного пользователя
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TagViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class AuthorSubscriptionViewset(viewsets.ModelViewSet):
    queryset = AuthorSubscription.objects.all()
    serializer_class = AuthorSubscriptionSerialaser
