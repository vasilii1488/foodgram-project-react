# from http import HTTPStatus
# from rest_framework.generics import get_object_or_404
# from rest_framework.response import Response
# from rest_framework import status

# from .models import Recipe


# # def remov_obj(model, user, pk):
# #     recipe = get_object_or_404(Recipe, id=pk)
# #     if not model.objects.filter(user=user, recipe__id=recipe).exists():
# #         return Response('Рецепт отсутствует в избранном',
# #                         status=status.HTTP_400_BAD_REQUEST)
# #     obj = model.objects.get(user=user, recipe__id=recipe)
# #     obj.delete()
# #     return Response(status=status.HTTP_204_NO_CONTENT)


# # def add_obj(model, user, pk):
# #     recipe = get_object_or_404(Recipe, id=pk)
# #     if model.objects.filter(user=user, id=pk).exists():
# #         return Response('Рецепт добавлен в список',
# #                         status=status.HTTP_400_BAD_REQUEST)
# #     obj = model.objects.create(user=user, id=pk)
# #     serializer = FavoriteSerializer(obj)
# #     return Response(serializer.data, status=status.HTTP_201_CREATED)
# def add_obj(self, request, *args, **kwargs):
#         """
#         Метод создания модели корзины или избранных рецептов.
#         A method for creating a basket model or selected recipes.
#         """
#         recipe_id = int(self.kwargs['recipes_id'])
#         recipe = get_object_or_404(Recipe, id=recipe_id)
#         if self.model.objects.filter(user=request.user,
#                                      recipe=recipe).exists():
#             return Response({
#                 'errors': 'Рецепт уже добавлен в список'
#             }, status=status.HTTP_400_BAD_REQUEST)
#         self.model.objects.create(user=request.user, recipe=recipe)
#         return Response(HTTPStatus.CREATED)

# def remov_obj(self, request, *args, **kwargs):
#         """
#         Метод удаления объектов модели корзины или избранных рецептов.
#         Method for deleting objects of the basket model or favorite recipes.
#         """
#         recipe_id = self.kwargs['recipes_id']
#         user_id = request.user.id
#         object = get_object_or_404(
#             self.model, user__id=user_id, recipe__id=recipe_id)
#         object.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
