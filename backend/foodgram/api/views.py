from rest_framework import viewsets
from posts.models import Recipes, Ingredients
from api import serializers
from django_filters.rest_framework import DjangoFilterBackend


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = serializers.RecipesSerializer


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = serializers.IngredientsSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name',)