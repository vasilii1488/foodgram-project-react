from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from users.serializers import CustomUserSerializer
from users.models import CustomUser
from .models import Tag, Ingredient, Recipe, Favorite, ShopList, Follow
from .serializers import (TagSerializer, IngredientSerializer,
                          FollowSerializer,
                          RecipeSerializer, RecipesCreateSerializer,
                          UserFollowSerializer,
                          RecipeFollowSerializer, FollowCreateSerializer)
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework import status, viewsets
from djoser.views import UserViewSet


class CustomUserViewSet(UserViewSet):
    """ Вьюсет для модели пользователя с дополнительным операциями
        через GET запросы. """

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = PageNumberPagination

    def get_permissions(self):
        if self.action == 'me':
            return (IsAuthenticated(),)
        return super().get_permissions()

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


class RecipeView(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
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

    @action(detail=True, url_path='favorite', methods=['POST', 'GET'],
            permission_classes=[IsAuthenticated])
    def recipe_id_favorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if Favorite.objects.filter(user=user, recipes=recipe).exists():
            return Response('Рецепт уже добавлен в избранное',
                            status=status.HTTP_400_BAD_REQUEST)
        favorite = Favorite.objects.create(user=user, recipes=recipe)
        serializer = RecipeFollowSerializer(favorite.recipes)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @recipe_id_favorite.mapping.delete
    def recipe_id_favorite_del(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if not Favorite.objects.filter(user=user, recipes=recipe).exists():
            return Response('Рецепт отсутствует в избранном',
                            status=status.HTTP_400_BAD_REQUEST)
        favorite = Favorite.objects.get(user=user, recipes=recipe)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, url_path='shopping_cart', methods=['POST', 'GET'],
            permission_classes=[IsAuthenticated])
    def recipe_cart(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if ShopList.objects.filter(customer=user, recipe=recipe).exists():
            return Response('Рецепт уже добавлен в список покупок',
                            status=status.HTTP_400_BAD_REQUEST)
        add_cart = ShopList.objects.create(customer=user, recipe=recipe)
        serializer = RecipeFollowSerializer(add_cart.recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @recipe_cart.mapping.delete
    def recipe_cart_del(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if not ShopList.objects.filter(customer=user,
                                       recipe=recipe).exists():
            return Response('Рецепт отсутствует в списке покупок',
                            status=status.HTTP_400_BAD_REQUEST)
        recipe_cart = ShopList.objects.get(customer=user, recipe=recipe)
        recipe_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
