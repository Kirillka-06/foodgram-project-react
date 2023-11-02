from rest_framework import exceptions
from django_filters import FilterSet
from django_filters.rest_framework import filters, CharFilter

from foods.models import Ingredient, Recipe, Tag


class IngredientSearchFilter(FilterSet):
    """
    FilterSet-класс для фильтрации поиска запросов
    на ингредиенты по заданным параметрам.
    """

    name = CharFilter(
        field_name='name',
        lookup_expr='istartswith'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilterSet(FilterSet):
    """
    FilterSet-класс для фильтрации запросов на рецепты
    по заданным параметрам.
    """

    author = filters.NumberFilter(field_name='author')
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = filters.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'author',
            'tags',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def get_is_favorited(self, queryset, field_name, value):
        if self.request.user.is_anonymous:
            raise exceptions.PermissionDenied()
        if value:
            return queryset.filter(
                favorite_recipe__user=self.request.user
            )
        return queryset

    def get_is_in_shopping_cart(self, queryset, field_name, value):
        if self.request.user.is_anonymous:
            raise exceptions.PermissionDenied()
        if value:
            return queryset.filter(
                shoppinglist_recipe__user=self.request.user
            )
        return queryset
