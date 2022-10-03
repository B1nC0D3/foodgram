from django.contrib import admin
from posts.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                          Subscribe, Tag, TagRecipe, Shopping_cart)


class IngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class TagInline(admin.TabularInline):
    model = TagRecipe
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientInline, TagInline)
    list_display = ('id', 'author', 'name', 'tag')
    readonly_fields = ('favorite_count',)
    list_filter = ('tags',)
    search_fields = ('author__username', 'name')

    def tag(self, obj):
        result = []
        for tag in obj.tags.all():
            result.append(tag.name)
        return result

    def favorite_count(self, obj):
        return Favorite.objects.filter(recipe=obj).count()


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name', )
    list_filter = ('measurement_unit',)


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')
    search_fields = ('recipe__name', 'user__username', 'user__email')
    list_filter = ('recipe__tags',)


class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('author', 'follower')
    search_fields = ('follower__username', 'follower__email')


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')
    search_fields = ('user__username', 'user__email', 'recipe__name')

admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Subscribe, SubscribeAdmin)
admin.site.register(Shopping_cart, ShoppingCartAdmin)