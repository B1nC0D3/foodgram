from posts.models import Recipes
import django_filters


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.CharFilter(field_name='tags__name', lookup_expr='iexact')
    class Meta:
        model = Recipes
        fields = ('tags',)