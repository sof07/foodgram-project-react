from recipes.views import (RecipeViewset,
                           UserViewSet,
                           TokenObtainPairView,
                           RegistrationView,
                           TagViewset, IngredientViewset)
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers


router = routers.DefaultRouter()
router.register(r'recipes', RecipeViewset, basename='recipes')
#router.register(r'users', RegistrationView, basename='users')
router.register(r'tags', TagViewset, basename='tags')
router.register(r'ingredients', IngredientViewset, basename='ingredients')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/', include('djoser.urls')),  # Работа с пользователями
    # path('api/', include('djoser.urls.authtoken')),  # Работа с токенами
    # path('api/auth/token/', TokenObtainPairView.as_view(
    #     serializer_class=TokenObtainPairSerializer), name='token'),
    # path('api/auth/signup/', RegistrationView.as_view(), name='signup')
]
