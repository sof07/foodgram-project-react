from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from .models import Recipe
from .serializers import RecipeSerialaser


class RecipeViewset(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerialaser()
