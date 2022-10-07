from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from .models import Recipe
from .serializers import RecipeFollowSerializer


def remov_obj(model, user, pk):
    recipe = get_object_or_404(Recipe, id=pk)
    if not model.objects.filter(user=user, recipe=recipe).exists():
        return Response('Рецепт отсутствует в избранном',
                        status=status.HTTP_400_BAD_REQUEST)
    obj = model.objects.get(user=user, recipe=recipe)
    obj.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


def add_obj(model, user, pk):
    recipe = get_object_or_404(Recipe, id=pk)
    if model.objects.filter(user=user, recipe=recipe).exists():
        return Response('Рецепт добавлен в список',
                        status=status.HTTP_400_BAD_REQUEST)
    obj = model.objects.create(user=user, recipe=recipe)
    serializer = RecipeFollowSerializer(obj.recipe)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
