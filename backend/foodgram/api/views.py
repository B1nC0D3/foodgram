from api import serializers
from api.filters import RecipeFilter
from api.permissions import IsAdminAuthorOrReadOnly
from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from posts.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                          Shopping_cart, Tag)
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

GET_SERIALIZER_REQUESTS = ['retrieve', 'list', 'destroy']
CONTENT_TYPE = 'text/plain'


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAdminAuthorOrReadOnly,)

    def get_serializer_class(self):
        if self.action in GET_SERIALIZER_REQUESTS:
            return serializers.GetRecipesSerializer
        return serializers.PostRecipesSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def _create_favorite(self, recipe, request):
        if Favorite.objects.filter(recipe=recipe, user=request.user).exists():
            return (
                {'errors': 'Этот рецепт уже добавлен в избранное'}, 
                status.HTTP_400_BAD_REQUEST)
        fav = Favorite.objects.create(recipe=recipe, user=request.user)
        serializer = serializers.FavoriteSerializer(fav, context={'request': request})
        return serializer.data, status.HTTP_201_CREATED

    def _delete_favorite(self, recipe, request):
        favorite = Favorite.objects.filter(recipe=recipe, user=request.user)
        if not favorite.exists():
            return (
                {'errors': 'Вы уже удалили этот рецепт из избранного'}, 
                status.HTTP_400_BAD_REQUEST)
        favorite.delete()
        return None, status.HTTP_204_NO_CONTENT

    @action(
        methods=('POST', 'DELETE'), detail=True, 
        permission_classes=(IsAuthenticated,),
        )
    def favorite(self, request, pk=None):
        recipe = Recipe.objects.get(id=pk)
        if request.method == 'POST':
            data, status = self._create_favorite(recipe, request)
            return Response(data, status=status)
        data, status = self._delete_favorite(recipe, request)
        return Response(data, status=status)

    def _add_to_shopping_cart(self, recipe, request):
        if Shopping_cart.objects.filter(
            recipe=recipe, user=request.user).exists():
            return (
                {'errors': 'Вы уже добавили этот рецепт в корзину'}, 
                status.HTTP_400_BAD_REQUEST)
        unit = Shopping_cart.objects.create(recipe=recipe, user=request.user)
        serializer = serializers.FavoriteSerializer(unit, context={'request': request})
        return serializer.data, status.HTTP_201_CREATED

    def _delete_from_shopping_cart(self, recipe, request):
        shopping_cart = Shopping_cart.objects.filter(recipe=recipe, user=request.user)
        if not shopping_cart.exists():
            return (
                {'errors': 'Вы уже удалили этот рецепт из корзины'}, 
                status.HTTP_400_BAD_REQUEST)
        shopping_cart.delete()
        return None, status.HTTP_204_NO_CONTENT

    @action(
        methods=('POST', 'DELETE'), detail=True, 
        permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        recipe = Recipe.objects.get(id=pk)
        if request.method == 'POST':
            data, status = self._add_to_shopping_cart(recipe, request)
            return Response(data, status=status)
        data, status = self._delete_from_shopping_cart(recipe, request)
        return Response(data, status=status)

    @action(methods=('GET',), detail=False, permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        result = HttpResponse(status=status.HTTP_200_OK, content_type=CONTENT_TYPE)
        ingredients = RecipeIngredient.objects.filter(
            recipe__shop_recipe__user=request.user).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount')).order_by()
        print(ingredients)
        for ingredient in ingredients:
            result.write(
                f'{ingredient["ingredient__name"]}' 
                f' ({ingredient["ingredient__measurement_unit"]}) - {ingredient["amount"]} \n')
        return result 


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientsSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = (AllowAny,)


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = serializers.TagsSerializer
    pagination_class = None
    permission_classes = (AllowAny,)
