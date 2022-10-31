from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from .models import Recipe
from .serializers import RecipeFollowSerializer


def remov_obj(self, model, user, pk):
    obj = model.objects.filter(user=user, recipe__id=pk)
    if obj.exists():
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response({
        'errors': 'Рецепт уже удален'
    }, status=status.HTTP_400_BAD_REQUEST)


def add_obj(self, model, user, pk):
    recipe = get_object_or_404(Recipe, id=pk)
    if model.objects.filter(user=user, recipe__id=pk).exists():
        return Response('Рецепт добавлен в список',
                        status=status.HTTP_400_BAD_REQUEST)
    model.objects.create(user=user, recipe=recipe)
    serializer = RecipeFollowSerializer(recipe)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
