from rest_framework import (filters, permissions,
                            serializers, status, viewsets)
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.tokens import default_token_generator
from .models import Recipe, Ingredient, Tag
from .serializers import (RecipeSerializer,
                          UserSerializer,
                          IngredientSerializer,
                          TagSerialaser)
from users.models import CustomUser
from rest_framework.decorators import action
from .permissions import IsAdmin
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.mail import send_mail
from django.conf import settings
from rest_framework_simplejwt import serializers as jwt_serializers
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.views import TokenObtainPairView


class TokenObtainPairView(TokenObtainPairView):
    serializer_class = jwt_serializers.TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        if request.data.get('username'):
            get_object_or_404(
                CustomUser, username=request.data.get('username'))
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data
        return Response({'token': token})


class IngredientViewset(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewset(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    # permission_classes = [IsAuthenticated]


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления пользователями.
    """

    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    permission_classes = [IsAdmin, ]
    search_fields = ('username',)
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=[permissions.IsAuthenticated, ]
    )
    def me(self, request):
        """
        Обработчик действия "me" для получения
        и обновления данных текущего пользователя.
        """

        user = CustomUser.objects.get(pk=request.user.id)
        serializer = self.serializer_class(
            user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(role=request.user.role)
        return Response(serializer.data)


class TagViewset(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerialaser
