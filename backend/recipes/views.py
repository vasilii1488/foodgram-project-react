from django.db.models import Sum
from django.http.response import HttpResponse
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
# from rest_framework.generics import get_object_or_404
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework import status, permissions
from http import HTTPStatus
from django_filters.rest_framework import DjangoFilterBackend

from .filters import AuthorAndTagFilter, IngredientSearchFilter
from users.models import CustomUser
from users.serializers import CustomUserSerializer
from .models import (Favorite, Follow, Ingredient, Recipe,
                     ShopList, Tag, RecipeIngredient)
from .serializers import (FollowSerializer,
                          IngredientSerializer,
                          RecipesCreateSerializer, RecipeSerializer,
                          TagSerializer, ShoppingCartSerializer, )
from .permissions import IsAuthorOrAdminOrReadOnly
# from .utils import remov_obj, add_obj


class CustomUserViewSet(UserViewSet):
    """ Вьюсет для модели пользователя с дополнительным операциями
        через GET запросы. """

    serializer_class = CustomUserSerializer

    def get_queryset(self):
        return CustomUser.objects.all()


class TagView(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None


class IngredientView(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    search_fields = ('^name',)
    pagination_class = None
    filter_backends = (IngredientSearchFilter,)


class RecipeView(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthorOrAdminOrReadOnly]
    queryset = Recipe.objects.all()
    pagination_class = PageNumberPagination
    pagination_class.page_size = 6
    filter_class = AuthorAndTagFilter
    filter_backends = [DjangoFilterBackend, ]

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PUT', 'PATCH'):
            return RecipesCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class BaseFavoriteCartViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthorOrAdminOrReadOnly]

    def create(self, request, *args, **kwargs):
        """
        Метод создания модели корзины или избранных рецептов.
        A method for creating a basket model or selected recipes.
        """
        recipe_id = int(self.kwargs['recipes_id'])
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if self.model.objects.filter(user=request.user,
                                     recipe=recipe).exists():
            return Response({
                'errors': 'Рецепт уже добавлен в список'
            }, status=status.HTTP_400_BAD_REQUEST)
        self.model.objects.create(user=request.user, recipe=recipe)
        return Response(HTTPStatus.CREATED)

    def delete(self, request, *args, **kwargs):
        """
        Метод удаления объектов модели корзины или избранных рецептов.
        Method for deleting objects of the basket model or favorite recipes.
        """
        recipe_id = self.kwargs['recipes_id']
        user_id = request.user.id
        object = get_object_or_404(
            self.model, user__id=user_id, recipe__id=recipe_id)
        object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(BaseFavoriteCartViewSet):
    """
    Вьюсет обработки модели корзины.
    Basket model processing viewset.
    """
    serializer_class = ShoppingCartSerializer
    queryset = ShopList.objects.all()
    model = ShopList


class FavoriteViewSet(BaseFavoriteCartViewSet):
    """
    Вьюсет обработки модели избранных рецептов.
    The viewset for processing the model of selected recipes.
    """
    serializer_class = ShoppingCartSerializer
    queryset = Favorite.objects.all()
    model = Favorite

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


class SubscribeViewSet(viewsets.ModelViewSet):
    """
    Вьюсет обработки моделей подписок.
    Viewset for processing subscription models.
    """
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return get_list_or_404(CustomUser, following__user=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Метод создания подписки.
        The method of creating a subscription.
        """
        user_id = self.kwargs.get('users_id')
        user = get_object_or_404(CustomUser, id=user_id)
        Follow.objects.create(
            user=request.user, following=user)
        return Response(HTTPStatus.CREATED)

    def delete(self, request, *args, **kwargs):
        """
        Метод удаления подписок.
        Method of deleting subscriptions.
        """
        author_id = self.kwargs['users_id']
        user_id = request.user.id
        subscribe = get_object_or_404(
            Follow, user__id=user_id, following__id=author_id)
        subscribe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
