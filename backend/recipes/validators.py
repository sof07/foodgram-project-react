from rest_framework import serializers


def validate_tags(self, data):
    if not data:
        raise serializers.ValidationError(
            'Должен быть хотя бы 1 тэг')
    if len(set(data)) != len(data):
        raise serializers.ValidationError('Тэги не должны повторяться')
    return data


def validate_ingredients(self, data):
    if not data or not any('id' in ingredient_data
                           for ingredient_data in data):
        raise serializers.ValidationError(
            'Рецепт не может быть без ингридиентов '
        )
    unique_ingredients = []
    for ingredient_data in data:
        ingredient_id = ingredient_data['id']
        if ingredient_id in [ingredient['id']
                             for ingredient in unique_ingredients]:
            raise serializers.ValidationError(
                'Ингредиенты должны быть уникальными.')
        unique_ingredients.append(ingredient_data)
    return data
