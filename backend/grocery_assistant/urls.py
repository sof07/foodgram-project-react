from recipes.views import RecipeViewset
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'recipe', RecipeViewset)
# router.register(r'achievements', AchievementViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls))
    # path('api/', include('djoser.urls')),  # Работа с пользователями
    # path('api/', include('djoser.urls.authtoken')),  # Работа с токенами
]
