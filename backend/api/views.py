from api.filters import RecipeFilterSet
from api.permissions import IsAuthorOrReadOnly
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from foods.models import (Favorite, Ingredient, IngredientForRecipe, Recipe,
                          ShoppingCart, Tag)
from foods.serializers import (CreateRecipeSerializer, IngredientSerializer,
                               RecipeSerializer, TagSerializer)
from rest_framework import (filters, generics, pagination, permissions, status,
                            views, viewsets)
from rest_framework.response import Response
from users.models import Subscription
from users.serializers import ShortRecipeSerializer, SubscriptionSerializer

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    View-класс для взаимодействия с моделью Tag.
    GET-запросы.
    """

    queryset = Tag.objects.all().order_by('id')
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    View-класс для взаимодействия с моделью Ingredient.
    Get-запросы.
    """

    queryset = Ingredient.objects.all().order_by('id')
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None

    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """
    View-класс для взаимодействия с моделью Recipe.
    GET-, POST-, PATCH- и DELETE-запросы.
    """

    queryset = Recipe.objects.all().order_by('id')
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilterSet

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        elif self.action in ('create', 'partial_update'):
            return CreateRecipeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context


class ListAPISubscription(generics.ListAPIView):
    """
    View-класс для взаимодействия с моделью Subscription.
    GET-запросы.
    """

    serializer_class = SubscriptionSerializer
    pagination_class = pagination.PageNumberPagination
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        author = User.objects.filter(
            following_authors__follower=self.request.user
        ).all()
        return author


class APISubscription(views.APIView):
    """
    View-класс для взаимодействия с моделью Subscription.
    POST- и DELETE-запросы.
    """

    def post(self, request, id):
        user = self.request.user
        if user.is_anonymous:
            return Response(
                {'detail': 'Учетные данные не были предоставлены.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        author = get_object_or_404(User, id=id)
        if Subscription.objects.filter(
            author=author,
            follower=self.request.user
        ).exists() or author == self.request.user:
            return Response(
                {'errors': ('Ошибка подписки на пользователя. '
                            'Подписка на себя или вы уже подписаны.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = SubscriptionSerializer(
            author,
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            Subscription.objects.create(
                author=author,
                follower=self.request.user
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        user = self.request.user
        if user.is_anonymous:
            return Response(
                {'detail': 'Учетные данные не были предоставлены.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

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

    def post(self, request, id):
        user = self.request.user
        if user.is_anonymous:
            return Response(
                {'detail': 'Учетные данные не были предоставлены.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        recipe = get_object_or_404(Recipe, id=id)
        if Favorite.objects.filter(
            user=self.request.user,
            recipe=recipe
        ).exists():
            return Response(
                {'errors': 'Вы уже добавили в избранное этот рецепт'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = ShortRecipeSerializer(
            recipe,
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            Favorite.objects.create(user=self.request.user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        user = self.request.user
        if user.is_anonymous:
            return Response(
                {'detail': 'Учетные данные не были предоставлены.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        recipe = get_object_or_404(Recipe, id=id)
        favorite = Favorite.objects.filter(
            user=self.request.user,
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

    def get(self, request):
        user = self.request.user
        if user.is_anonymous:
            return Response(
                {'detail': 'Учетные данные не были предоставлены.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        ingredients = IngredientForRecipe.objects.filter(
            recipe__shoppinglist_recipe__user=user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(sum=Sum('amount'))
        shopping_cart = ''
        shopping_list = ShoppingCart.objects.filter(user=user)

        print(f'ingredients: {ingredients}')
        print(f'shopping_list: {shopping_list}')
        for ingredient in ingredients:
            shopping_cart += (
                f'{ingredient["ingredient__name"]} - '
                f'{ingredient["sum"]} '
                f'{ingredient["ingredient__measurement_unit"]}\n'
            )
        response = HttpResponse(shopping_cart, content_type='text/plain')
        return response

    def post(self, request, id):
        user = self.request.user
        if user.is_anonymous:
            return Response(
                {'detail': 'Учетные данные не были предоставлены.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        recipe = get_object_or_404(Recipe, id=id)
        if ShoppingCart.objects.filter(
            user=self.request.user,
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
            ShoppingCart.objects.create(user=self.request.user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        user = self.request.user
        if user.is_anonymous:
            return Response(
                {'detail': 'Учетные данные не были предоставлены.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        recipe = get_object_or_404(Recipe, id=id)
        Favorite = ShoppingCart.objects.filter(
            user=self.request.user,
            recipe=recipe
        )
        if Favorite.exists():
            Favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Вы не добавляли этот рецепт в список покупок.'},
            status=status.HTTP_400_BAD_REQUEST
        )
