from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from recipes.views import (CustomUserViewSet, IngredientViewset, RecipeViewSet,
                           TagViewset)
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'tags', TagViewset, basename='tags')
router.register(r'ingredients', IngredientViewset, basename='ingredients')
router.register(r'users', CustomUserViewSet, basename='users')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    re_path(r'api/auth/', include('djoser.urls.authtoken')),


]
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
