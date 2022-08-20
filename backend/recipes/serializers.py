from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from users.models import CustomUser
from users.serializers import CustomUserSerializer
from .models import (Tag, Ingredient, Recipe, RecipeIngredient,
                     Favorite, ShopList, Follow)
from rest_framework.validators import UniqueTogetherValidator


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('__all__')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('__all__')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount',)

    def get_id(self, obj):
        return obj.ingredient.id

    def get_name(self, obj):
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(many=True)
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        if self.context['request'].user.is_authenticated:
            current_user = self.context['request'].user
            return Favorite.objects.filter(user=current_user,
                                           recipes=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        if 'request' not in self.context:
            raise serializers.ValidationError('Invalid request')
        if self.context['request'].user.is_authenticated:
            current_user = self.context['request'].user
            return ShopList.objects.filter(customer=current_user,
                                           recipe=obj).exists()


class CreateIngredientRecipeSerializer(serializers.ModelSerializer):
    """ Сериализатор для модели Ингредиенты в рецептах. """

    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipesCreateSerializer(serializers.ModelSerializer):
    """ Сериализатор для создания объекторв модели Рецепты,
        с настроенными методами создания и обновления. """

    author = CustomUserSerializer(read_only=True)
    ingredients = CreateIngredientRecipeSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            temp = RecipeIngredient.objects.create(
                ingredient=Ingredient.objects.get(pk=ingredient['id']),
                amount=ingredient['amount'])
            recipe.ingredients.add(temp)
        for tag in tags:
            recipe.tags.add(tag)
        return recipe

    def update(self, instance, validated_data):
        instance.ingredients.clear()
        instance.tags.clear()
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        for ingredient in ingredients:
            temp = RecipeIngredient.objects.create(
                ingredient=Ingredient.objects.get(
                    pk=ingredient['id']),
                amount=ingredient['amount'])
            instance.ingredients.add(temp)
        instance.tags.clear()
        for tag in tags:
            instance.tags.add(tag)
        return super().update(instance, validated_data)


class RecipeFollowSerializer(RecipeSerializer):
    """ Сериализатор модели Рецепты для корректного отображения
        в подписках. """

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserFollowSerializer(CustomUserSerializer):
    """ Сериализатор модели Пользователя, для корректного отображения
        в подписках. """
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')
        model = CustomUser

    def get_recipes(self, obj):
        request = self.context['request']
        limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj)
        if limit:
            queryset = queryset[:int(limit)]
            return RecipeFollowSerializer(queryset, many=True).data
        return RecipeFollowSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        recipes = Recipe.objects.filter(author=obj)
        return recipes.count()


class FollowSerializer(serializers.ModelSerializer):
    """ Создаем сериализатор для подписок. """

    email = serializers.ReadOnlyField(source='following.email')
    id = serializers.ReadOnlyField(source='following.id')
    username = serializers.ReadOnlyField(source='following.email')
    first_name = serializers.ReadOnlyField(source='following.first_name')
    last_name = serializers.ReadOnlyField(source='following.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')
        model = Follow

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(
            user=obj.user, following=obj.following
        ).exists()

    def get_recipes(self, obj):
        request = self.context['request']
        limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj.following)
        if limit:
            queryset = queryset[:int(limit)]
        return RecipeFollowSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.following).count()


class FollowCreateSerializer(serializers.ModelSerializer):
    """ Сериализатор создания объекта Подписки. """

    class Meta:
        fields = ('user', 'following')
        model = Follow
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=['user', 'following'],
                message=['user_in_flw']
            )
        ]

    def validate(self, data):
        user = data['user']
        current_follow = data['following']
        if user == current_follow:
            raise serializers.ValidationError(
                ['flw_self'])
        return data
