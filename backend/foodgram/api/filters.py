from posts.models import Recipes, Tags
import django_filters


class RecipeFilter(django_filters.FilterSet):

    def _get_choices():
        tags = Tags.objects.all()
        result = []
        for tag in tags:
            result.append((tag.name, tag.name))
        return result
            

    tags = django_filters.MultipleChoiceFilter(field_name='tags__name', choices=_get_choices())
    is_favorited = django_filters.NumberFilter(field_name='is_favorited', method='get_is_favorited')
    class Meta:
        model = Recipes
        fields = ('tags', 'author', 'is_favorited')

    def get_is_favorited(self, queryset, name, value):
        remove_recipes = []
        for recipe in queryset:
            check_fav = recipe.recipe.filter(user=self.request.user)
            if len(check_fav) == 0:
                remove_recipes.append(recipe.id)
        return Recipes.objects.exclude(id__in=remove_recipes)
            

    

    