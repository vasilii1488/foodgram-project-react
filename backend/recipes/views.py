from django.db.models import Sum
from django.http.response import HttpResponse
from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly
from .filters import IngredientSearchFilter, RecipeFilter
from .models import (Follow, Ingredient, Recipe, Favorite,
                     Tag, RecipeIngredient, ShopList)
from .serializers import (FollowSerializer,
                          IngredientSerializer,
                          RecipesCreateSerializer, RecipeSerializer,
                          TagSerializer)
from .utils import remov_obj, add_obj


User = get_user_model()


class CustomUserViewSet(UserViewSet):
    pagination_class = PageNumberPagination

    @action(detail=True, permission_classes=[IsAuthenticated],
            methods=['POST'])
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)

        if user == author:
            return Response({
                'errors': 'Вы не можете подписываться на самого себя'
            }, status=status.HTTP_400_BAD_REQUEST)
        if Follow.objects.filter(user=user, following=author).exists():
            return Response({
                'errors': 'Вы уже подписаны на данного пользователя'
            }, status=status.HTTP_400_BAD_REQUEST)

        follow = Follow.objects.create(user=user, following=author)
        serializer = FollowSerializer(
            follow, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def del_subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        if user == author:
            return Response({
                'errors': 'Вы не можете отписываться от самого себя'
            }, status=status.HTTP_400_BAD_REQUEST)
        follow = Follow.objects.filter(user=user, following=author)
        if follow.exists():
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({
            'errors': 'Вы уже отписались'
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        queryset = Follow.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagView(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None


class IngredientView(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Ingredient.objects.all()
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)
    pagination_class = None


class RecipeView(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    permission_classes = [IsOwnerOrReadOnly]
    pagination_class = PageNumberPagination
    pagination_class.page_size = 6
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PUT', 'PATCH'):
            return RecipesCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


    @action(detail=True, url_path='favorite', methods=['POST', 'GET'])
    def recipe_id_favorite(self, request, pk=None):
        """ Метод добавления рецепта в избранное. """
        user = request.user
        model = Favorite
        return add_obj(model=model, user=user, pk=pk)

    @recipe_id_favorite.mapping.delete
    def recipe_id_favorite_del(self, request, pk):
        user = request.user
        model = Favorite
        return remov_obj(model=model, user=user, pk=pk)

    @action(detail=True, url_path='shopping_cart', methods=['POST'],
            permission_classes=[IsOwnerOrReadOnly])
    def recipe_cart(self, request, pk):
        """ Метод добавления рецепта в список покупок. """
        user = request.user
        model = ShopList
        return add_obj(model=model, user=user, pk=pk)

    @recipe_cart.mapping.delete
    def recipe_cart_del(self, request, pk):
        user = request.user
        model = ShopList
        return remov_obj(model=model, user=user, pk=pk)

    @action(detail=False,
            url_path='download_shopping_cart',
            methods=['GET'],
            permission_classes=[IsAuthenticated])
    def download_cart_recipe(self, request):
        """ Метод скачивания списка продуктов. """
        ingredients_list = RecipeIngredient.objects.filter(
            recipe__favor__user=request.user
        ).values('ingredient__name', 'ingredient__measurement_unit').order_by(
            'ingredient__name').annotate(tolal_sum=Sum('amount'))
        response = HttpResponse(ingredients_list, 'Content-Type: text/plain')
        response['Content-Disposition'] = 'attachment; filename=cart_recipe'
        return response
