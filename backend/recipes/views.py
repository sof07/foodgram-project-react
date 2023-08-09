from rest_framework import (filters, permissions, viewsets)

from .models import Recipe, Ingredient, Tag
from users.models import AuthorSubscription
from .serializers import (RecipeSerializer,
                          IngredientSerializer,
                          TagSerializer,
                          AuthorSubscriptionSerialaser,
                          )

from rest_framework.response import Response
from django.conf import settings


class IngredientViewset(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    search_fields = ('name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class TagViewset(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class AuthorSubscriptionViewset(viewsets.ModelViewSet):
    queryset = AuthorSubscription.objects.all()
    serializer_class = AuthorSubscriptionSerialaser
