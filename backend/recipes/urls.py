from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TagView, IngredientView, RecipeView

router = DefaultRouter()
router.register('tags', TagView, basename='tags')
router.register('ingredients', IngredientView, basename='ingredients')
router.register('recipes', RecipeView, basename='resipes')

urlpatterns = [
    path('', include(router.urls)),
]