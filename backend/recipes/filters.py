from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter

from .models import Recipe, Tag, Favorite, ShopList


User = get_user_model()


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'


class AuthorAndTagFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug',
    )
    is_favorited = filters.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart')

    class Meta:
        """
        Мета параметры фильтров модели рецептов.
        """
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        queryset = Favorite.objects.all()
        if value and not self.request.user.is_anonymous:
            return queryset.filter(recipes__favor__user_id=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        queryset = ShopList.objects.all()
        if value and not self.request.user.is_anonymous:
            return queryset.filter(recipes__cart_recipe__user_id=self.request.user)
        return queryset
