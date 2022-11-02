from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from .models import Recipe


def remov_obj(model, user, pk):
    obj = model.objects.filter(user=user, recipe__id=pk)
    if obj.exists():
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response({
        'errors': 'Рецепт уже удален'
    }, status=status.HTTP_400_BAD_REQUEST)


def add_obj(pk, model, user):
    if model.objects.filter(user=user, recipe__id=pk).exists():
        return Response({
            'errors': 'Рецепт уже добавлен в список'
        }, status=status.HTTP_400_BAD_REQUEST)
    recipe = get_object_or_404(Recipe, id=pk)
    model.objects.create(user=user, recipe=recipe)
    return Response(status=status.HTTP_201_CREATED)
