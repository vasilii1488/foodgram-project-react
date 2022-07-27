from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from users.serializers import CustomUserSerializer
from .models import Tag, Ingredient, Recipe, RecipeIngredient
from django.conf import settings
import requests


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
    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )


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

    