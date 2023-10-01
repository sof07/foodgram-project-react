from django.test import TestCase
from users.models import CustomUser

from .models import Ingredient, Recipe, Tag


class RecipeModelTestCase(TestCase):
    def setUp(self):
        # Создаем тестового пользователя
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpassword'
        )

        # Создаем тестовый тэг
        self.tag = Tag.objects.create(
            name='Test Tag',
            color='red'
        )

        # Создаем тестовый ингредиент
        self.ingredient = Ingredient.objects.create(
            name='Test Ingredient',
            measurement_unit='grams'
        )

    def test_create_recipe(self):
        # Создаем тестовый рецепт
        recipe = Recipe.objects.create(
            author=self.user,
            name='Test Recipe',
            text='Test Recipe Description',
            cooking_time=30
        )
        recipe.tags.add(self.tag)
        recipe.ingredients.add(self.ingredient)

        # Проверяем, что рецепт был создан успешно
        self.assertEqual(recipe.name, 'Test Recipe')
        self.assertEqual(recipe.text, 'Test Recipe Description')
        self.assertEqual(recipe.cooking_time, 30)
        self.assertEqual(recipe.tags.count(), 1)
        self.assertEqual(recipe.ingredients.count(), 1)

    def test_is_favorited(self):
        # Создаем тестовый рецепт и добавляем его в избранное для пользователя
        recipe = Recipe.objects.create(
            author=self.user,
            name='Test Recipe',
            text='Test Recipe Description',
            cooking_time=30
        )
        recipe.tags.add(self.tag)
        recipe.ingredients.add(self.ingredient)

        self.user.profile.favorite_recipes.add(recipe)

        # Проверяем, что рецепт находится в избранном для пользователя
        self.assertTrue(recipe.is_favorited(self.user))

    def test_is_in_shopping_cart(self):
        # Создаем тестовый рецепт и добавляем его в корзину покупок
        recipe = Recipe.objects.create(
            author=self.user,
            name='Test Recipe',
            text='Test Recipe Description',
            cooking_time=30
        )
        recipe.tags.add(self.tag)
        recipe.ingredients.add(self.ingredient)

        self.user.profile.shopping_cart_recipes.add(recipe)

        # Проверяем, что рецепт находится в корзине покупок для пользователя
        self.assertTrue(recipe.is_in_shopping_cart(self.user))
