from rest_framework import serializers
from .models import Recipe


class RecipeSerialaser(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = 'autor', 'title', 'description', 'date', 'cooking_time', 'ingredients', 'tag'
