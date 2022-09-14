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
    class Meta:
        model = Recipes
        fields = ('tags', 'author')
    

    