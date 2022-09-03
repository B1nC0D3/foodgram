from django.core.paginator import Paginator
from django.shortcuts import render
from posts.models import Recipes


def index(request):
    recipe_list = Recipes.objects.all()
    paginator = Paginator(recipe_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'src/main/index.js', context)
