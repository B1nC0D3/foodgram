from django.contrib import admin
from posts.models import Recipe, Ingredient, Tag, RecipeIngredient, TagRecipe, Favorite, Subscribe


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


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')
    


class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('author', 'follower')


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Subscribe, SubscribeAdmin)