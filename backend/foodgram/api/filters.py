from posts.models import Recipe, Tag
import django_filters


def _get_choices():
    try:
        tags = Tag.objects.all()
        result = []
        for tag in tags:
            result.append((tag.name, tag.name))
        return result
    except Exception:
        return (None, None)

class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.MultipleChoiceFilter(field_name='tags__name', choices=_get_choices())
    is_favorited = django_filters.NumberFilter(field_name='is_favorited', method='get_is_favorited')
    is_in_shopping_cart = django_filters.NumberFilter(field_name='is_in_shopping_cart', method='get_is_in_shopping_cart')
    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited')

    def get_is_favorited(self, queryset, name, value):
        remove_recipes = []
        for recipe in queryset:
            check_fav = recipe.recipe.filter(user=self.request.user)
            if len(check_fav) == 0:
                remove_recipes.append(recipe.id)
        return Recipe.objects.exclude(id__in=remove_recipes)
    
    def get_is_in_shopping_cart(self, queryset, name, value):
        remove_recipes = []
        for recipe in queryset:
            check_in_cart = recipe.shop_recipe.filter(user=self.request.user)
            if len(check_in_cart) == 0:
                remove_recipes.append(recipe.id)
        return Recipe.objects.exclude(id__in=remove_recipes)
    