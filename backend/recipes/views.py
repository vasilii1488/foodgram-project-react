from django.db.models import Sum
from django.http.response import HttpResponse
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from .permissions import IsOwnerOrReadOnly
from users.models import CustomUser
from users.serializers import CustomUserSerializer
from .models import (Follow, Ingredient, Recipe, Favorite,
                     ShopList, Tag, RecipeIngredient)
from .serializers import (FollowCreateSerializer, FollowSerializer,
                          IngredientSerializer,
                          RecipeSerializer, RecipesCreateSerializer,
                          TagSerializer, UserFollowSerializer)
from .utils import remov_obj, add_obj


class CustomUserViewSet(UserViewSet):
    """ Вьюсет для модели пользователя с дополнительным операциями
        через GET запросы. """

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = PageNumberPagination

    @action(detail=True, url_path='subscribe')
    def user_subscribe_add(self, request, id):
        user = request.user
        following = get_object_or_404(CustomUser, pk=id)
        serializer = FollowCreateSerializer(
            data={'user': user.id, 'following': id})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        follow = get_object_or_404(Follow, user=user, following=following)
        serializer = UserFollowSerializer(follow.following,
                                          context={'request': request})
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
    search_fields = ('^name',)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly)
    queryset = Recipe.objects.all()
    pagination_class = PageNumberPagination
    pagination_class.page_size = 6
    permission_classes = [IsOwnerOrReadOnly]

    def get_serializer_class(self):
        """
        Метод выбора сериализатора в зависимости от запроса.
        The method of selecting the serializer depending on the request.
        """
        if self.request.method == 'GET':
            return RecipeSerializer
        else:
            return RecipesCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, url_path='favorite', methods=['POST'],
            permission_classes=[IsAuthenticated]
            )
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
            permission_classes=[])
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
            recipe__cart_recipe__user=request.user
        ).values('ingredient__name', 'ingredient__measurement_unit').order_by(
            'ingredient__name').annotate(tolal_sum=Sum('amount'))
        response = HttpResponse(ingredients_list, 'Content-Type: text/plain')
        response['Content-Disposition'] = 'attachment; filename=cart_recipe'
        return response
