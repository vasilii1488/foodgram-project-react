import datetime
from django.http.response import HttpResponse
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response


from users.models import CustomUser
from users.serializers import CustomUserSerializer
from .pagination import LimitPageNumberPagination
from .filters import IngredientSearchFilter, RecipeFilter
from .models import (Favorite, Follow, Ingredient, Recipe,
                     ShopList, Tag, RecipeIngredient)
from .serializers import (FollowCreateSerializer, FollowSerializer,
                          IngredientSerializer, UserFollowSerializer,
                          RecipesCreateSerializer, RecipeSerializer,
                          TagSerializer)
from .utils import remov_obj, add_obj


class CustomUserViewSet(UserViewSet):
    """ Вьюсет для модели пользователя с дополнительным операциями
        через GET запросы. """
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = LimitPageNumberPagination

    @action(detail=True, methods=['POST'], url_path='subscribe')
    def user_subscribe_add(self, request, id):
        user = request.user
        following = get_object_or_404(CustomUser, pk=id)
        serializer = FollowCreateSerializer(
            data={'user': user.id, 'following': id},
            context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        follow = get_object_or_404(Follow, user=user, following=following)
        serializer = UserFollowSerializer(follow.following)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @user_subscribe_add.mapping.delete
    def user_subscribe_del(self, request, id):
        user = request.user
        following = get_object_or_404(CustomUser, pk=id)
        if not Follow.objects.filter(user=user,
                                     following=following).exists():
            return Response(['Вы не подписаны на этого пользователя'],
                            status=status.HTTP_400_BAD_REQUEST)
        follow = Follow.objects.get(user=user, following=following)
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False, url_path='subscriptions',
            permission_classes=[IsAuthenticated])
    def user_subscriptions(self, request):
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
    permission_classes = (IsAuthenticatedOrReadOnly,)
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
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Recipe.objects.all()
    filterset_class = RecipeFilter
    pagination_class = LimitPageNumberPagination

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PUT', 'PATCH'):
            return RecipesCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, url_path='favorite', methods=['POST'],
            permission_classes=[IsAuthenticated])
    def recipe_id_favorite(self, request, pk):
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
            permission_classes=[IsAuthenticated])
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
            methods=['GET'])
    def download_cart_recipe(self, request):
        """ Метод скачивания списка продуктов. """
        shopping_list = {}
        ingredients = RecipeIngredient.objects.filter(
            recipe__cart_recipe__user=request.user
        )
        for ingredient in ingredients:
            amount = ingredient.amount
            name = ingredient.ingredient.name
            measurement_unit = ingredient.ingredient.measurement_unit
            if name not in shopping_list:
                shopping_list[name] = {
                    'measurement_unit': measurement_unit,
                    'amount': amount
                }
            else:
                shopping_list[name]['amount'] += amount
        main_list = ([f"* {item}:{value['amount']}"
                      f"{value['measurement_unit']}\n"
                      for item, value in shopping_list.items()])
        today = datetime.date.today()
        main_list.append(f'\n Enjoy your meal, {today.year}')
        response = HttpResponse(main_list, 'Content-Type: text/plain')
        response['Content-Disposition'] = 'attachment; filename="BuyList.txt"'
        return response
