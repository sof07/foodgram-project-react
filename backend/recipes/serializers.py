from rest_framework import serializers
import base64
from .models import Recipe, Ingredient, Tag, IngredientRecipe, Favorite
from users.models import CustomUser, AuthorSubscription
import webcolors
from django.contrib.auth import authenticate
from rest_framework import serializers
from django.core.files.base import ContentFile
from djoser.serializers import TokenCreateSerializer as DjoserTokenCreateSerializer
from djoser.compat import get_user_email_field_name
from djoser.conf import settings
from django.db.models import Count


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
        read_only_fields = ['name', 'color', 'slug']


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


# class AuthorSerialaser(serializers.ModelSerializer):
#     is_subscribed = serializers.SerializerMethodField()

#     class Meta:
#         model = CustomUser
#         fields = ('email', 'id', 'username', 'first_name',
#                   'last_name', 'is_subscribed')

#     def get_is_subscribed(self, obj):
#         request = self.context.get('request')
#         if request and request.user == obj:
#             return obj.has_subscriptions()
#         return None


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


# class FollowingSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = AuthorSubscription
#         fields = ('id', 'subscriber')

# class FollowersSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = AuthorSubscription
#         fields = ('id', 'author')
class RecipeFavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class CustomUserSerializer(serializers.ModelSerializer):
    # это поле для чтения, связанное с определённым методом,
    # в котором будет вычислено значение этого поля.
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'password', 'is_subscribed')
        extra_kwargs = {'password': {'write_only': True}}

    """
    Давайте разберем его подробнее:

        obj в этом контексте представляет собой объект модели, 
        который вы пытаетесь сериализовать или получить информацию о нем. 
        В вашем случае, это, возможно, объект Author (или другой объект, 
        который имеет связь с AuthorSubscription).

        subscribers и subscriber - это связи, определенные в модели AuthorSubscription:

        subscriber - это внешний ключ (ForeignKey) к модели пользователя 
        (settings.AUTH_USER_MODEL), который указывает на пользователя, 
        который подписывается на другого пользователя.

        subscribers - это внешний ключ (ForeignKey) к модели пользователя 
        (settings.AUTH_USER_MODEL), который указывает на пользователя, 
        на которого подписываются.

        obj.subscribers - это обращение к связанному менеджеру, 
        который предоставляется Django для отношений, созданных с 
        использованием ForeignKey. Он позволяет получить доступ ко всем записям, 
        связанным с obj через поле subscribers в модели AuthorSubscription.

        .filter(subscriber=user) - это метод фильтрации, который выполняет 
        фильтрацию записей в таблице AuthorSubscription. Мы хотим найти все записи, 
        где поле subscriber (то есть, пользователь, который подписывается) 
        равно user (текущий пользователь).

        .exists() - это метод, который вызывается после .filter(). 
        Он возвращает булево значение True, если хотя бы одна запись 
        соответствует фильтру, и False, если нет. В данном случае, 
        мы используем .exists(), чтобы проверить, существует ли хотя бы одна запись, 
        где текущий пользователь (user) подписан на объект, представленный obj.

        Итак, obj.subscribers.filter(subscriber=user).exists() позволяет вам проверить, 
        существует ли запись в таблице AuthorSubscription, в которой текущий 
        пользователь (user) подписан на объект, представленный obj. Если такая запись 
        существует, метод вернет True, что может использоваться, например, для 
        определения, подписан ли пользователь на автора.
    """

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return obj.subscribers.filter(subscriber=user).exists()


class SubscribeUserSerializer(serializers.ModelSerializer):
    # это поле для чтения, связанное с определённым методом,
    # в котором будет вычислено значение этого поля.
    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeFavoriteSerializer(many=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False

        return obj.subscribers.filter(subscriber=user).exists()

    def get_recipes_count(self, obj):
        recipe_count = obj.recipes.aggregate(Count("id"))
        return recipe_count["id__count"]


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
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

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
    # Для получения тэга в нужном виде

    def to_representation(self, instance):

        data = super().to_representation(instance)
        tags_data = TagSerializer(instance.tags.all(), many=True).data
        data['tags'] = tags_data
        return data

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return obj.favorites.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return obj.shopping_cart.filter(user=user).exists()


# class AuthorSubscriptionSerializer(serializers.ModelSerializer):
#     # author = CustomUserSerializer(read_only=True)

#     class Meta:
#         model = AuthorSubscription
#         fields = ('username',)


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all()
    )
    name = serializers.CharField(
        read_only=True,
        source='recipe.name'
    )
    image = serializers.CharField(
        read_only=True,
        source='recipe.image'
    )
    cooking_time = serializers.CharField(
        read_only=True,
        source='recipe.cooking_time'
    )

    class Meta:
        model = Favorite
        fields = ['id', 'name', 'image', 'cooking_time']
