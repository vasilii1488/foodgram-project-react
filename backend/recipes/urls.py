from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CustomUserViewSet, IngredientView, RecipeViewSet, TagView

router = DefaultRouter()
router.register('users', CustomUserViewSet, basename='users')
router.register('tags', TagView, basename='tags')
router.register('ingredients', IngredientView, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='resipes')

urlpatterns = [
    path('', include(router.urls)),
]
