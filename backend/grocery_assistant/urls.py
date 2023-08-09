from recipes.views import (RecipeViewSet,
                           TagViewset, IngredientViewset, AuthorSubscriptionViewset)
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from rest_framework import routers


router = routers.DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'tags', TagViewset, basename='tags')
router.register(r'ingredients', IngredientViewset, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'subscriptions', AuthorSubscriptionViewset,
                basename='subscriptions')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/', include('djoser.urls')),
    # Работа с пользователями
    re_path(r'api/auth/', include('djoser.urls.authtoken')),
]
