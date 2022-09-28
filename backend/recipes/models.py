from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Tag(models.Model):
    """ Модель Тег. """

    name = models.CharField(max_length=200,
                            unique=True,
                            verbose_name='Название тега')
    color = models.CharField(max_length=7,
                             unique=True,
                             verbose_name='Цвет тега')
    slug = models.SlugField(max_length=200,
                            unique=True,
                            verbose_name='Ссылка тега')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return f"{self.name}"


class Ingredient(models.Model):
    """ Модель Ингредиент. """

    name = models.CharField(max_length=200,
                            verbose_name='Название ингредиента')
    measurement_unit = models.CharField(max_length=200,
                                        verbose_name='Единица измерения')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f"{self.name}"


class Recipe(models.Model):
    """ Модель Рецепт. """
    tags = models.ManyToManyField(Tag,
                                  related_name='recipes',
                                  verbose_name='Тег рецепта')
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE,
                               verbose_name='Автор рецепта')
    ingredients = models.ManyToManyField(Ingredient,
                                         through='RecipeIngredient',
                                         verbose_name='Ингредиенты',
                                         related_name='recipes',)
    name = models.CharField(max_length=200,
                            verbose_name='Название рецепта')
    image = models.ImageField(verbose_name='Фото рецепта')
    text = models.TextField(verbose_name='Описание рецепта')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        default=1,
        validators=[MinValueValidator(1, message='Не может быть равно нулю')])

    class Meta:
        ordering = ['-id']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class RecipeIngredient(models.Model):
    """ Модель для связи Рецептов и Ингредиентов. """
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_in_recipe')
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE,
                                   related_name='ingredients_in_recipe',
                                   verbose_name='Ингредиент')
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиентов',
        default=1,
        validators=[MinValueValidator(1, message='Не может быть равно нулю')]
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецетах'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient')]

    def __str__(self):
        return (f"{self.ingredient.name}"
                f"{self.amount} {self.ingredient.measurement_unit} ")


class Follow(models.Model):
    """ Модель для Подписок. """
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='follower')
    following = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  on_delete=models.CASCADE,
                                  related_name='following')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_following')]


class Favorite(models.Model):
    """ Модель для Избранного. """
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='user')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='favor')

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe')]


class ShopList(models.Model):
    """ Модель для Листа Покупок. """

    customer = models.ForeignKey(settings.AUTH_USER_MODEL,
                                 on_delete=models.CASCADE,
                                 related_name='customer')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='cart_recipe')

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['customer', 'recipe'],
                name='unique_customer_recipe')]
