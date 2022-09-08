from rest_framework import serializers
from posts.models import Recipes, Ingredients, Tags, RecipeIngredient
import base64
from django.core.files.base import ContentFile
from users.serializers import CustomUserSerializer


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredients


class IngredientRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'amount')
        model = RecipeIngredient


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tags

class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            name = imgstr[:10].replace('/', '')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f'{name}.{ext}')
        return super().to_internal_value(data)


class RecipesSerializer(serializers.ModelSerializer):
    # author = serializers.SlugRelatedField(slug_field='username', read_only=True)
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = IngredientRecipeSerializer(many=True, read_only=True)
    tags = TagsSerializer(read_only=True, many=True)
    class Meta:
        fields = (
            'author', 'name', 'image',
            'text', 'ingredients',
            'tags', 'cooking_time'
            )
        model = Recipes

    # def create(self, validated_data):
    #     ingredients = validated_data.pop('ingredients')
    #     recipe = Recipes.objects.create(**validated_data)
    #     for ingredient in ingredients:
    #         current_ingredient, status = Ingredients.objects.get(**ingredient)
    #         RecipeIngredient.objects.create(ingredient=current_ingredient, recipe=recipe)
    #     return recipe
