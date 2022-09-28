from api import serializers
from api.filters import RecipeFilter
from api.permissions import IsAdminAuthorOrReadOnly, IsAdminOrReadOnly
from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from posts.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                          Shopping_cart, Tag)
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

GET_REQUESTS = ['retrieve', 'list', 'destoy']


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAdminAuthorOrReadOnly,)

    def get_serializer_class(self):
        if self.action in GET_REQUESTS:
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
        recipes = Shopping_cart.objects.filter(user=request.user)
        ingredient_list = {}
        cart_recipes = []
        ingredient_recipe = set()
        for recipe in recipes:
            ingredients = recipe.recipe.amount.all()
            cart_recipes.append(recipe.recipe)
            for ingredient in ingredients:
                ingredient_recipe.add(ingredient.ingredient)
            for ingredient in ingredient_recipe:
                amount = RecipeIngredient.objects.filter(
                    recipe__in=cart_recipes, ingredient=ingredient.ingredient).aggregate(Sum('amount'))
                key = f'{ingredient.ingredient.name} ({ingredient.ingredient.measurement_unit})'
                ingredient_list[key] = amount['amount__sum']
    
        result = HttpResponse(status=status.HTTP_200_OK, content_type='text/plain')
        for key, value in ingredient_list.items():
            result.write(f'{key} - {value} \n')
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
