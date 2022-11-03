from django_filters import rest_framework as django_filter
from rest_framework import filters

from users.models import CustomUser
from recipes.models import Recipe, Favorite, ShopList


class RecipeFilters(django_filter.FilterSet):
    """
    Настройка фильтров модели рецептов.
    """
    author = django_filter.ModelChoiceFilter(queryset=CustomUser.objects.all())
    tags = django_filter.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = django_filter.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = django_filter.BooleanFilter(
        method='get_is_in_shopping_cart')

    class Meta:
        """
        Мета параметры фильтров модели рецептов.
        """
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, name, value):
        queryset = Favorite.objects.all()
        if value and not self.request.user.is_anonymous:
            return queryset.filters(recipes__favor__user_id=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, name, value):
        queryset = ShopList.objects.all()
        if value and not self.request.user.is_anonymous:
            return queryset.filter(recipes__cart_recipe__user_id=self.request.user)
        return queryset


class IngredientSearchFilter(filters.SearchFilter):

    search_param = 'name'
