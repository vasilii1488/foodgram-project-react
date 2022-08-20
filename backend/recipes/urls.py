from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TagView, IngredientView, RecipeView, CustomUserViewSet

router = DefaultRouter()
router.register('users', CustomUserViewSet, basename='users')
router.register('tags', TagView, basename='tags')
router.register('ingredients', IngredientView, basename='ingredients')
router.register('recipes', RecipeView, basename='resipes')

urlpatterns = [
    path('', include(router.urls)),
]
