from rest_framework import viewsets, permissions, filters
from posts.models import Recipes, Ingredients, Tags
from api import serializers
from rest_framework.pagination import PageNumberPagination
from api.filters import RecipeFilter
from django_filters.rest_framework import DjangoFilterBackend

GET_REQUESTS = ['retrieve', 'list', 'destoy']



class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (permissions.AllowAny,)

    def get_serializer_class(self):
        if self.action in GET_REQUESTS:
            return serializers.GETRecipesSerializer
        else:
            return serializers.POSTRecipesSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    

class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = serializers.IngredientsSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = (permissions.AllowAny,)


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = serializers.TagsSerializer
    pagination_class = None
    permission_classes = (permissions.AllowAny,)
