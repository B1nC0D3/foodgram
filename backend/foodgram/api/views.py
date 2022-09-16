from rest_framework import viewsets, permissions, filters, status
from posts.models import Recipes, Ingredients, Tags, Favorite
from api import serializers
from rest_framework.decorators import action
from api.filters import RecipeFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response

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
    
    def _create_favorite(self, recipe, request):
        if Favorite.objects.filter(recipe=recipe, user=request.user).exists():
            return {'errors': 'Этот рецепт уже добавлен в избранное'}, status.HTTP_400_BAD_REQUEST
        fav = Favorite.objects.create(recipe=recipe, user=request.user)
        serializer = serializers.FavoriteSerializer(fav, context={'request': request})
        return serializer.data, status.HTTP_201_CREATED

    def _delete_favorite(self, recipe, request):
        if not Favorite.objects.filter(recipe=recipe, user=request.user).exists():
            return {'errors': 'Вы уже удалили этот рецепт из избранного'}, status.HTTP_400_BAD_REQUEST
        Favorite.objects.get(recipe=recipe, user=request.user).delete()
        return None, status.HTTP_204_NO_CONTENT

    @action(methods=('POST', 'DELETE'), detail=True)
    def favorite(self, request, pk=None):
        recipe = Recipes.objects.get(id=pk)
        if request.method == 'POST':
            data, status = self._create_favorite(recipe, request)
            return Response(data, status=status)
        data, status = self._delete_favorite(recipe, request)
        return Response(data, status=status)
        
        

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
