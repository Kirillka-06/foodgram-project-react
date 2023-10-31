from rest_framework.routers import DefaultRouter

from django.urls import path, include

from api.views import (TagViewSet,
                       IngredientViewSet,
                       RecipeViewSet,
                       APIFavorite,
                       APIShoppingCart,
                       APISubscription,
                       ListAPISubscription)


food = DefaultRouter()
food.register('tags', TagViewSet)
food.register('ingredients', IngredientViewSet)
food.register('recipes', RecipeViewSet)

urlpatterns = [
    path('recipes/download_shopping_cart/', APIShoppingCart.as_view()),
    path('recipes/<int:id>/shopping_cart/', APIShoppingCart.as_view()),
    path('recipes/<int:id>/favorite/', APIFavorite.as_view()),
    path('', include(food.urls)),

    path('users/subscriptions/', ListAPISubscription.as_view()),
    path('users/<int:id>/subscribe/', APISubscription.as_view()),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
