from recipes.views import (RecipeViewSet,
                           TagViewset, IngredientViewset, CustomUserViewSet)
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from rest_framework import routers
from django.conf.urls.static import static


router = routers.DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'tags', TagViewset, basename='tags')
router.register(r'ingredients', IngredientViewset, basename='ingredients')
router.register(r'users', CustomUserViewSet, basename='users')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/', include('djoser.urls')),
    re_path(r'api/auth/', include('djoser.urls.authtoken')),


]
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
