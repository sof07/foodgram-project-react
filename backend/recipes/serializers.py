from rest_framework import serializers
from .models import Recipe, Ingredient, Tag, IngredientRecipe
from users.models import CustomUser
from .validators import validate_email, validate_username


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели User.
    Поля:
    - username: CharField. Имя пользователя.
    - email: EmailField. Email пользователя.
    - first_name: CharField. Имя пользователя.
    - last_name: CharField. Фамилия пользователя.
    - bio: CharField. Биография пользователя.
    - role: CharField. Роль пользователя.
    Наследуется от:
    - ModelSerializer. Сериализатор модели User.
    Модель:
    - User. Модель пользователя.
    """
    email = serializers.EmailField(required=True, validators=[
        validate_email,
    ])
    username = serializers.SlugField(required=True, validators=[
        validate_username,
    ])

    class Meta:
        model = CustomUser
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  # 'is_subscribed'
                  )

    def validate_role(self, value):
        for key, val in CustomUser.Role.choices:
            if value == key:
                return value
        raise serializers.ValidationError("Неверный тип пользователя.")

    def validate_first_name(self, value):
        if len(value) > 150:
            raise serializers.ValidationError("first_name слишком длинное.")
        return value

    def validate_last_name(self, value):
        if len(value) > 150:
            raise serializers.ValidationError("last_name слишком длинное.")
        return value

    def validate(self, data):
        email = data.get('email')
        username = data.get('username')
        if (CustomUser.objects.filter(username=username).exists()
                and CustomUser.objects.get(username=username).email != email):
            raise serializers.ValidationError(
                "Пользователь и email не совпадают!"
            )
        if (CustomUser.objects.filter(email=email).exists()
                and not CustomUser.objects.filter(username=username).exists()):
            raise serializers.ValidationError(
                "Данный email уже занят!"
            )
        return data


class SignupSerializer(UserSerializer):
    """
    Сериализатор для регистрации пользователя.
    Наследуется от UserSerializer.
    """

    class Meta:
        model = CustomUser
        extra_kwargs = {'password': {'write_only': True}}
        fields = ('email',
                  'username',
                  'first_name',
                  'last_name',
                  'password',)

class TagSerialaser(serializers.ModelSerializer):
    class Meta:

        model = Tag
        fields = ('id',
                  'name',
                  'color',
                  'slug')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer()

    class Meta:
        model = IngredientRecipe
        fields = ('amount', 'ingredient',)


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True, source='ingredient')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id',  'tags', 'author', 'ingredients', 'name', 'image',
                  'text', 'cooking_time', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return obj.is_favorited(user) if user.is_authenticated else False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return obj.is_in_shopping_cart(user) if user.is_authenticated else False

    def get_ingredients(self, obj):
        recipe_ingredients = IngredientRecipe.objects.filter(recipe=obj)
        serializer = IngredientRecipeSerializer(recipe_ingredients, many=True)
        return serializer.data


class SubscriptionSerializer(serializers.ModelSerializer):
    recipes = RecipeSerializer(many=True, source='author.recipes')

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count']
