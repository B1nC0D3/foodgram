from posts.models import Recipes, Tags
import django_filters


def get_choices():
    tags = Tags.objects.all()
    result = []
    for tag in tags:
        result.append((tag.name, tag.name))
    print(result)
    return result

class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.MultipleChoiceFilter(field_name='tags__name', choices=get_choices())
    class Meta:
        model = Recipes
        fields = ('tags', 'author')
    