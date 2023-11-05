from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from rest_framework.generics import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, status, views, viewsets
from rest_framework.response import Response

from users.models import Subscription
from foods.models import (Favorite, Ingredient, IngredientForRecipe, Recipe,
                          ShoppingCart, Tag)
from .filters import IngredientSearchFilter, RecipeFilterSet
from .pagination import CustomPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (CreateRecipeSerializer, IngredientSerializer,
                          RecipeSerializer, ShortRecipeSerializer,
                          SubscriptionSerializer, TagSerializer)

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    View-класс для взаимодействия с моделью Tag.
    GET-запросы.
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    View-класс для взаимодействия с моделью Ingredient.
    Get-запросы.
    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None

    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientSearchFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """
    View-класс для взаимодействия с моделью Recipe.
    GET-, POST-, PATCH- и DELETE-запросы.
    """

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilterSet

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        elif self.action in ('create', 'partial_update'):
            return CreateRecipeSerializer


class ListAPISubscription(generics.ListAPIView):
    """
    View-класс для взаимодействия с моделью Subscription.
    GET-запросы.
    """

    serializer_class = SubscriptionSerializer
    pagination_class = CustomPagination
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return User.objects.filter(
            following_authors__follower=self.request.user
        )


class APISubscription(views.APIView):
    """
    View-класс для взаимодействия с моделью Subscription.
    POST- и DELETE-запросы.
    """

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, id):
        user = self.request.user
        author = get_object_or_404(User, id=id)
        if Subscription.objects.filter(
            author=author,
            follower=user
        ).exists() or author == user:
            return Response(
                {'errors': ('Ошибка подписки на пользователя. '
                            'Подписка на себя или вы уже подписаны.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = SubscriptionSerializer(
            author,
            context={'request': request}
        )
        Subscription.objects.create(
            author=author,
            follower=user
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        user = self.request.user
        author = get_object_or_404(User, id=id)
        subscription = Subscription.objects.filter(
            author=author,
            follower=user
        )
        if subscription.exists():
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Вы не были подписаны на этого пользователя'},
            status=status.HTTP_400_BAD_REQUEST
        )


class APIFavorite(views.APIView):
    """
    View-класс для взаимодействия с моделью Favorite.
    POST- и DELETE-запросы.
    """

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, id):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=id)
        if Favorite.objects.filter(
            user=user,
            recipe=recipe
        ).exists():
            return Response(
                {'errors': 'Вы уже добавили в избранное этот рецепт'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = ShortRecipeSerializer(
            recipe,
            context={'request': request}
        )
        Favorite.objects.create(user=user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=id)
        favorite = Favorite.objects.filter(
            user=user,
            recipe=recipe
        )
        if favorite.exists():
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Вы не добавляли этот рецепт в избранное.'},
            status=status.HTTP_400_BAD_REQUEST
        )


class APIShoppingCart(views.APIView):
    """
    View-класс для взаимодействия с моделью ShoppingCart.
    GET-, POST- и DELETE-запросы.
    """

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = self.request.user
        ingredients = IngredientForRecipe.objects.filter(
            recipe__shoppinglist_recipe__user=user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(sum=Sum('amount'))

        unique_ingredients = {}
        for ingredient in ingredients:
            if (ingredient['ingredient__name'] not in unique_ingredients.keys()
                or ingredient.get('ingredient__measurement_unit')
                    != unique_ingredients.get(
                        ingredient['ingredient__name'])[1]):
                unique_ingredients[ingredient['ingredient__name']] = [
                    ingredient['sum'],
                    ingredient['ingredient__measurement_unit']
                ]
            else:
                unique_ingredients[ingredient['ingredient__name']][0] \
                    += ingredient['sum']

        shopping_cart = ''
        for ingredient_name, ingredient_values in unique_ingredients.items():
            shopping_cart += (
                f'{ingredient_name} - '
                f'{ingredient_values[0]} '
                f'{ingredient_values[1]}\n'
            )
        return HttpResponse(shopping_cart, content_type='text/plain')

    def post(self, request, id):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=id)
        if ShoppingCart.objects.filter(
            user=user,
            recipe=recipe
        ).exists():
            return Response(
                {'errors': ('Вы уже добавили'
                            'в список покупок'
                            'этот рецепт.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = ShortRecipeSerializer(
            recipe,
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            ShoppingCart.objects.create(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=id)
        Favorite = ShoppingCart.objects.filter(
            user=user,
            recipe=recipe
        )
        if Favorite.exists():
            Favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Вы не добавляли этот рецепт в список покупок.'},
            status=status.HTTP_400_BAD_REQUEST
        )
