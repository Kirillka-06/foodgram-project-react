from django.contrib import admin

from foods.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'color',
        'slug'
    )


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit'
    )
    list_filter = (
        'name',
    )


class IngredientInline(admin.TabularInline):
    model = Recipe.ingredients.through


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        '_tags',
        'author',
        'name',
        'text',
        'cooking_time'
    )
    list_filter = (
        'name',
        'author',
        'tags'
    )

    inlines = (IngredientInline,)

    def _tags(self, row):
        return ','.join([x.name for x in row.tags.all()])


class FavouriteAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe'
    )


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe'
    )


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorite, FavouriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
