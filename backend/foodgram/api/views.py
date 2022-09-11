from rest_framework import viewsets, permissions, filters
from posts.models import Recipes, Ingredients, Tags
from api import serializers
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('tags__name',)
    permission_classes = (permissions.AllowAny,)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return serializers.GETRecipesSerializer
        else:
            return serializers.POSTRecipesSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = serializers.IngredientsSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = (permissions.AllowAny,)


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = serializers.TagsSerializer
    permission_classes = (permissions.AllowAny,)
