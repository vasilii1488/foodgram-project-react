from tokenize import blank_re
from django.core.validators import MinValueValidator
from django.db import models
from django.conf import settings


class Tag(models.Model):
    """ Модель Тег. """

    name = models.CharField(max_length=200, unique=True)
    color = models.CharField(max_length=7, unique=True)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return f"{self.name}"


class Ingredient(models.Model):
    """ Модель Ингредиент. """

    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f"{self.name}"


class RecipeIngredient(models.Model):
    """ Модель для связи Рецептов и Ингредиентов. """

    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1, message='Не может быть равно нулю')]
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецетах'

    def __str__(self):
        return (f"{self.ingredient.name}  "
                f"{self.amount}{self.ingredient.measurement_unit} ")


class Recipe(models.Model):
    """ Модель Рецепт. """
    tags = models.ManyToManyField(Tag, related_name='tags')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ingredients = models.ManyToManyField(RecipeIngredient,
                                         related_name='ingredients')
    is_favorited = models.BooleanField(default=False)
    is_in_shopping_cart = models.BooleanField(default=False)
    name = models.CharField(max_length=200)
    image = models.ImageField(blank=True, null=True)
    text = models.TextField()
    cooking_time = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1, message='Не может быть равно нулю')]
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class Follow(models.Model):
    """ Модель для Подписок. """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='follower')
    following = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                  related_name='following')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'


class Favorite(models.Model):
    """ Модель для Избранного. """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='user')
    recipes = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                                related_name='favor')

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class ShopList(models.Model):
    """ Модель для Листа Покупок. """

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name='customer')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='cart_recipe')

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'


