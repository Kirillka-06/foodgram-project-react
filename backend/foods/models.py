from django.contrib.auth import get_user_model
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True
    )
    color = models.CharField(
        max_length=7,
        default='',
        unique=True,
        validators=[
            RegexValidator(
                '^#([a-fA-F0-9]{6})',
                message='Поле должно содержать HEX-код цвета.',
            )
        ]
    )
    slug = models.SlugField(
        max_length=200,
        unique=True
    )

    class Meta:
        ordering = ('id',)

    def __str__(self) -> str:
        return (f'Tag. id: {self.id} '
                f'название : {self.name[:20]}')


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=200)

    class Meta:
        ordering = ('id',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient'
            )
        ]

    def __str__(self) -> str:
        return (f'Ingredient. id: {self.id} '
                f'название: {self.name[:20]}')


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        related_name='recipe_tags'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientForRecipe',
        related_name='recipe_ingredients'
    )
    name = models.CharField(max_length=200)
    image = models.ImageField(
        upload_to='',
        default=''
    )
    text = models.TextField()
    cooking_time = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1, 'Cooking_time должно быть больше 1'),
            MaxValueValidator(10000, 'Да что вы там такое готовите?')
        ]
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self) -> str:
        return (f'Recipe. id: {self.id} '
                f'название: {self.name[:25]}')


class TagForRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='tag_for_recipe'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ('id',)
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'tag'],
                name='unique_tags_in_recipe'
            )
        ]

    def __str__(self) -> str:
        return (f'TagForRecipe. Рецепт: {self.recipe} '
                f'тег: {self.tag}')


class IngredientForRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredient'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient'
    )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(1, 'Amount должно быть больше 1')]
    )

    class Meta:
        ordering = ('id',)
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredients_in_recipe'
            )
        ]

    def __str__(self) -> str:
        return (f'IngredientForRecipe. Рецепт: {self.recipe} '
                f'Ингредиент: {self.ingredient}')


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_follower'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipe'
    )

    class Meta:
        ordering = ('id',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]

    def __str__(self) -> str:
        return (f'Favorite. Подписчик рецепта: {self.user} '
                f'рецепт: {self.recipe}')


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shoppinglist_user'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shoppinglist_recipe'
    )

    class Meta:
        ordering = ('id',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shoppinglist'
            )
        ]

    def __str__(self) -> str:
        return (f'ShoppingCart. Пользователь: {self.user} '
                f'рецепт: {self.recipe}')
