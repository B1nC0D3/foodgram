from rest_framework import serializers
from posts.models import Recipes, Ingredients, Tags, RecipeIngredient, TagRecipe
import base64
from django.core.files.base import ContentFile
from users.serializers import CustomUserSerializer


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredients.objects.all())
    class Meta:
        
        fields = ('id', 'amount')
        model = RecipeIngredient


class GETIngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit', default='asd')

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = RecipeIngredient


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredients


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


class GETRecipesSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = GETIngredientRecipeSerializer(source='amount', many=True)
    tags = TagsSerializer(many=True, read_only=True)
    class Meta:
        fields = (
            'author', 'name', 'image',
            'text', 'ingredients',
            'tags', 'cooking_time'
            )
        model = Recipes


class POSTRecipesSerializer(GETRecipesSerializer):
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tags.objects.all())
    ingredients = IngredientRecipeSerializer(source='amount', many=True)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('amount')
        recipe = Recipes.objects.create(**validated_data)
        for tag in tags:
            TagRecipe.objects.create(tag=tag, recipe=recipe)
        for ingredient in ingredients:
            RecipeIngredient.objects.create(ingredient=ingredient['id'], amount=ingredient['amount'], recipe=recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data['name']
        instance.text = validated_data['text']
        instance.cooking_time = validated_data['cooking_time']
        instance.image = validated_data['image']
        ingredients = validated_data.pop('amount')
        tags = validated_data.pop('tags')
        TagRecipe.objects.filter(recipe=instance).delete()
        RecipeIngredient.objects.filter(recipe=instance).delete()
        for tag in tags:
            TagRecipe.objects.create(tag=tag, recipe=instance)
        for ingredient in ingredients:
            RecipeIngredient.objects.create(ingredient=ingredient['id'], amount=ingredient['amount'], recipe=instance)
        return instance
