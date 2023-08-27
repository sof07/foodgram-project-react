from rest_framework import serializers
import base64
from .models import Recipe, Ingredient, Tag, IngredientRecipe
from users.models import CustomUser
from .validators import validate_email, validate_username
import webcolors
from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from djoser.serializers import TokenCreateSerializer as DjoserTokenCreateSerializer
from djoser.compat import get_user_email_field_name
from djoser.conf import settings
from .utils import base64_to_image, to_internal_value
import logging
from django.shortcuts import get_object_or_404


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        # read_only_fields = ['name', 'color', 'slug']


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)
# class Base64ImageField(serializers.ImageField):
#     """
#     A Django REST framework field for handling image-uploads through raw post data.
#     It uses base64 for encoding and decoding the contents of the file.

#     Heavily based on
#     https://github.com/tomchristie/django-rest-framework/pull/1268

#     Updated for Django REST framework 3.
#     """

#     def to_internal_value(self, data):
#         from django.core.files.base import ContentFile
#         import base64
#         import six
#         import uuid

#         # Check if this is a base64 string
#         if isinstance(data, six.string_types):
#             # Check if the base64 string is in the "data:" format
#             if 'data:' in data and ';base64,' in data:
#                 # Break out the header from the base64 content
#                 header, data = data.split(';base64,')

#             # Try to decode the file. Return validation error if it fails.
#             try:
#                 decoded_file = base64.b64decode(data)
#             except TypeError:
#                 self.fail('invalid_image')

#             # Generate file name:
#             # 12 characters are more than enough.
#             file_name = str(uuid.uuid4())[:12]
#             # Get the file name extension:
#             file_extension = self.get_file_extension(file_name, decoded_file)

#             complete_file_name = "%s.%s" % (file_name, file_extension, )

#             data = ContentFile(decoded_file, name=complete_file_name)

#         return super(Base64ImageField, self).to_internal_value(data)

#     def get_file_extension(self, file_name, decoded_file):
#         import imghdr

#         extension = imghdr.what(file_name, decoded_file)
#         extension = "jpg" if extension == "jpeg" else extension

#         return extension


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class AuthorSerialaser(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user == obj:
            return obj.has_subscriptions()
        return None


class CustomTokenCreateSerializer(serializers.Serializer):
    password = serializers.CharField(
        required=False, style={"input_type": "password"})

    default_error_messages = {
        "invalid_credentials": settings.CONSTANTS.messages.INVALID_CREDENTIALS_ERROR,
        "inactive_account": settings.CONSTANTS.messages.INACTIVE_ACCOUNT_ERROR,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

        self.email_field = get_user_email_field_name(CustomUser)
        self.fields[self.email_field] = serializers.EmailField()

    def validate(self, attrs):
        password = attrs.get("password")
        email = attrs.get("email")
        self.user = authenticate(
            request=self.context.get("request"), email=email, password=password
        )
        if not self.user:
            self.user = CustomUser.objects.filter(email=email).first()
            if self.user and not self.user.check_password(password):
                self.fail("invalid_credentials")
        if self.user and self.user.is_active:
            return attrs
        self.fail("invalid_account")


class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return obj.subscribers.filter(subscriber=user).exists()


class AuthorSubscriptionSerialaser(serializers.ModelSerializer):
    class Mets:
        fields = ('author')


# class RecipeSerializer(serializers.ModelSerializer):
#     tags = TagSerializer(many=True)
#     author = CustomUserSerializer()
#     # Используем source для связанных ингредиентов
#     ingredients = IngredientRecipeSerializer(
#         source='recipe_ingredients', many=True)
#     is_favorited = serializers.BooleanField()
#     is_in_shopping_cart = serializers.BooleanField()

#     class Meta:
#         model = Recipe
#         fields = (
#             'id', 'tags', 'author', 'ingredients', 'is_favorited', 'is_in_shopping_cart',
#             'name', 'image', 'text', 'cooking_time'
#         )


class RecipeIngridientsSerialaser(serializers.ModelSerializer):

    class Meta:
        fields = ['id', 'amount']


class RecipeCreateIngridientsSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    name = serializers.CharField(
        read_only=True,
        source='ingredient.name'
    )
    measurement_unit = serializers.CharField(
        read_only=True,
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientRecipe
        fields = ['id', 'name', 'measurement_unit', 'amount']


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = RecipeCreateIngridientsSerializer(
        many=True,
        source='recipe_ingredients'
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    image = Base64ImageField(required=False, allow_null=True)
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def create(self, validated_data):
        ingredients_data = validated_data.pop('recipe_ingredients')
        tags_data = validated_data.pop('tags')

        recipe = Recipe.objects.create(**validated_data)
        for ingredient_data in ingredients_data:
            IngredientRecipe.objects.create(
                recipe=recipe,
                ingredient_id=ingredient_data['id'].id,
                amount=ingredient_data['amount']
            )
        recipe.tags.set(tags_data)

        recipe.save()
        return recipe

    def update(self, recipe, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('recipe_ingredients')
        recipe.name = validated_data.get('name', recipe.name)
        recipe.text = validated_data.get('text', recipe.text)
        recipe.image = validated_data.get('image', recipe.image)
        recipe.recipe_ingredients.all().delete()
        for ingredient_data in ingredients_data:
            IngredientRecipe.objects.create(recipe=recipe,
                                            ingredient_id=ingredient_data['id'].id,
                                            amount=ingredient_data['amount']
                                            )

        recipe.tags.set(tags_data)
        recipe.save()
        return recipe


class SubscriptionSerializer(serializers.ModelSerializer):
    recipes = RecipeCreateIngridientsSerializer(
        many=True, source='author.recipes')

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count']
