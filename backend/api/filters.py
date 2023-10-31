from django_filters import FilterSet
from django_filters.rest_framework import filters
from foods.models import Recipe, Tag


class RecipeFilterSet(FilterSet):
    """
    Filter-класс для фильтрации запросов на рецепты
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
        print(f'fav: {value}')
        print(queryset)
        if value:
            return Recipe.objects.filter(
                favorite_recipe__user=self.request.user
            )
        return queryset

    def get_is_in_shopping_cart(self, queryset, field_name, value):
        print(f'shop: {value}')
        if value:
            return Recipe.objects.filter(
                shoppinglist_recipe__user=self.request.user
            )
        return queryset
