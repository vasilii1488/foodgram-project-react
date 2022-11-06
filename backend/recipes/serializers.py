from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from users.models import CustomUser
from users.serializers import CustomUserSerializer

from .models import (Follow, Ingredient, Recipe, RecipeIngredient, Tag,
                     Favorite, ShopList)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('__all__')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('__all__')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id',)
    name = serializers.ReadOnlyField(source='ingredient.name',)
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True,
        required=True, source='ingredients_in_recipe',)
    tags = TagSerializer(many=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_in_shopping_cart', 'is_favorited',
            'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user,
                                           recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShopList.objects.filter(user=user,
                                           recipe=obj).exists()

    def validate(self, data):
        if 'request' not in self.context:
            raise serializers.ValidationError('Invalid request')
        return data


class CreateIngredientRecipeSerializer(serializers.ModelSerializer):
    """ Сериализатор для модели Ингредиенты в рецептах. """

    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipesCreateSerializer(serializers.ModelSerializer):
    """ Сериализатор для создания объектов модели Рецепты,
        с настроенными методами создания и обновления. """

    author = CustomUserSerializer(read_only=True)
    ingredients = CreateIngredientRecipeSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time'
        )

    def validate(self, data):
        ingredients = data['ingredients']
        ingredient_list = []
        for items in ingredients:
            ingredient = Ingredient.objects.get(id=items['id'])
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    'Ингредиенты должны быть уникальными!')
            ingredient_list.append(ingredient)
        tags = data['tags']
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise serializers.ValidationError(
                    'Тэги должны быть уникальными!'
                )
            tags_list.append(tag)
        return data

    def create_ingredients(self, ingredients, recipe):
        create_ingredient = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=get_object_or_404(Ingredient, pk=ingredient["id"]),
                amount=ingredient['amount']
            )
            for ingredient in ingredients]
        RecipeIngredient.objects.bulk_create(create_ingredient)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.add(*tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.ingredients.clear()
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        self.create_ingredients(ingredients, instance)
        instance.tags.clear()
        for tag in tags:
            instance.tags.add(tag)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }).data


class RecipeFollowSerializer(serializers.ModelSerializer):
    """ Сериализатор модели Рецепты для корректного отображения
        в подписках. """

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowCreateSerializer(serializers.ModelSerializer):
    """ Сериализатор создания объекта Подписки. """
    user = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all())
    following = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all())

    class Meta:
        model = Follow
        fields = ('user', 'following')

    def validate(self, data):
        user = self.context.get('request').user
        following_id = data['following'].id
        if Follow.objects.filter(user=user,
                                 following=following_id,).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны!'
            )
        if user.id == following_id:
            raise serializers.ValidationError(
                'Вы не можете подписаться на самого себя!!'
            )
        return data


class UserFollowSerializer(CustomUserSerializer):
    """ Сериализатор модели Пользователя, для отображения
        в подписках. """
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')
        model = CustomUser

    def to_representation(self, instance):
        authors = FollowSerializer(instance.following, 
                                   context={'request': self.context.get('request')})
        return authors.data


class FollowSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='following.email')
    id = serializers.ReadOnlyField(source='following.id')
    username = serializers.ReadOnlyField(source='following.email')
    first_name = serializers.ReadOnlyField(source='following.first_name')
    last_name = serializers.ReadOnlyField(source='following.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(
            user=obj.user, following=obj.following).exists()

    def get_recipes(self, obj):
        request = self.context['request']
        limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj.following)
        if limit:
            queryset = queryset[:int(limit)]
        return RecipeFollowSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.following).count()
