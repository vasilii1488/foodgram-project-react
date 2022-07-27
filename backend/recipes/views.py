from rest_framework.permissions import AllowAny
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from .models import Tag, Ingredient, Recipe, RecipeIngredient
from .serializers import (TagSerializer, IngredientSerializer, 
                        RecipeSerializer, RecipesCreateSerializer) 
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework import mixins, status, viewsets
from django.http import HttpResponseRedirect


class TagView(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = [AllowAny, ]
    pagination_class = None


class IngredientView(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny, ]
    queryset = Ingredient.objects.all()
    pagination_class = None


class RecipeView(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    permission_classes = [AllowAny, ]
    queryset = Recipe.objects.all()
    pagination_class = PageNumberPagination
    pagination_class.page_size = 6

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PUT', 'PATCH'):
            return RecipesCreateSerializer
        return RecipeSerializer
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = RecipesCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = RecipesCreateSerializer(
            recipe, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    