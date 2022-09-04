from rest_framework import viewsets
from posts.models import Recipes
from api import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = serializers.RecipesSerializer
