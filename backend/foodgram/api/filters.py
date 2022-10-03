import django_filters
from django.db.utils import OperationalError
from posts.models import Recipe, Tag


def _get_choices():
    try:
        tags = Tag.objects.all()
        result = []
        for tag in tags:
            result.append((tag.slug, tag.slug))
        return result
    except Exception:
        return (None, None)
    


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.MultipleChoiceFilter(
        field_name='tags__slug', choices=_get_choices())
    is_favorited = django_filters.NumberFilter(
        field_name='is_favorited', method='get_is_favorited')
    is_in_shopping_cart = django_filters.NumberFilter(
        field_name='is_in_shopping_cart', method='get_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        remove_recipes = []
        for recipe in queryset:
            check_fav = recipe.recipes.filter(
                user=self.request.user).count()
            if check_fav == 0:
                remove_recipes.append(recipe.id)
        return Recipe.objects.exclude(id__in=remove_recipes)

    def get_is_in_shopping_cart(self, queryset, name, value):
        remove_recipes = []
        for recipe in queryset:
            print(recipe.shop_recipe.filter(user=self.request.user), '=================')
            check_in_cart = recipe.shop_recipe.filter(
                user=self.request.user).count()
            if check_in_cart == 0:
                remove_recipes.append(recipe.id)
        print(Recipe.objects.exclude(id__in=remove_recipes), '=========')
        return Recipe.objects.exclude(id__in=remove_recipes)
