from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CustomUserViewSet, IngredientView, RecipeView, TagView,
                    FavoriteViewSet, ShoppingCartViewSet, SubscribeViewSet)

router = DefaultRouter()
router.register('users', CustomUserViewSet, basename='users')
router.register('tags', TagView, basename='tags')
router.register('ingredients', IngredientView, basename='ingredients')
router.register('recipes', RecipeView, basename='resipes')

urlpatterns = [
    path('', include(router.urls)),
    path('recipes/<int:recipes_id>/favorite/',
         FavoriteViewSet.as_view({'post': 'create',
                                  'delete': 'delete'}), name='favorite'),
    path('recipes/<int:recipes_id>/shopping_cart/',
         ShoppingCartViewSet.as_view({'post': 'create',
                                     'delete': 'delete'}), name='cart'),
     path('users/<int:users_id>/subscribe/',
         SubscribeViewSet.as_view({'post': 'create',
                                   'delete': 'delete'}), name='subscribe'),
]
