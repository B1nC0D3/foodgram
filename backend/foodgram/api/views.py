from api import serializers
from api.filters import RecipeFilter
from api.permissions import IsAdminAuthorOrReadOnly, IsAdminOrReadOnly
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from posts.models import Favorite, Ingredient, Recipe, Shopping_cart, Tag
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

GET_REQUESTS = ['retrieve', 'list', 'destoy']


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAdminAuthorOrReadOnly,)

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

    @action(methods=('POST', 'DELETE'), detail=True, permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk=None):
        recipe = Recipe.objects.get(id=pk)
        if request.method == 'POST':
            data, status = self._create_favorite(recipe, request)
            return Response(data, status=status)
        data, status = self._delete_favorite(recipe, request)
        return Response(data, status=status)

    def _add_to_shopping_cart(self, recipe, request):
        if Shopping_cart.objects.filter(recipe=recipe, user=request.user).exists():
            return {'errors': 'Вы уже добавили этот рецепт в корзину'}, status.HTTP_400_BAD_REQUEST
        unit = Shopping_cart.objects.create(recipe=recipe, user=request.user)
        serializer = serializers.FavoriteSerializer(unit, context={'request': request})
        return serializer.data, status.HTTP_201_CREATED

    def _delete_from_shopping_cart(self, recipe, request):
        if not Shopping_cart.objects.filter(recipe=recipe, user=request.user).exists():
            return {'errors': 'Вы уже удалили этот рецепт из корзины'}, status.HTTP_400_BAD_REQUEST
        Shopping_cart.objects.get(recipe=recipe, user=request.user).delete()
        return None, status.HTTP_204_NO_CONTENT

    @action(methods=('POST', 'DELETE'), detail=True, permission_classes=(IsAuthenticated,))
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
        for recipe in recipes:
            ingredients = recipe.recipe.amount.all()
            for ingredient in ingredients:
                key = f'{ingredient.ingredient.name} ({ingredient.ingredient.measurement_unit})'
                print(key)
                if key not in ingredient_list:
                    ingredient_list[key] = ingredient.amount
                else:
                    ingredient_list[key] += ingredient.amount

        print(ingredient_list)
        result = open('Список покупок.txt', 'w+')
        for key, value in ingredient_list.items():
            result.write(f'{key} - {value} \n')
        result.close()
        response = open('Список покупок.txt')
        return HttpResponse(response, content_type='text/plain', status=status.HTTP_200_OK)


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientsSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = (IsAdminOrReadOnly,)


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = serializers.TagsSerializer
    pagination_class = None
    permission_classes = (IsAdminOrReadOnly,)
