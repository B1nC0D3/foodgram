import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from foodgram.settings import MEDIA_URL
from posts.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                          Shopping_cart, Subscribe, Tag, TagRecipe)
from rest_framework import serializers
from users.serializers import CustomUserSerializer
from rest_framework.validators import UniqueTogetherValidator
from django.db import transaction

User = get_user_model()


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:

        fields = ('id', 'amount')
        model = RecipeIngredient


class GetIngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = RecipeIngredient


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            name = imgstr[:10].replace('/', '')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f'{name}.{ext}')
        return super().to_internal_value(data)


class GetRecipesSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField(method_name='is_favorite')
    is_in_shopping_cart = serializers.SerializerMethodField(method_name='shopping_cart')
    author = CustomUserSerializer(read_only=True)
    image = serializers.SerializerMethodField(method_name='image_url')
    ingredients = GetIngredientRecipeSerializer(source='amount', many=True)
    tags = TagsSerializer(many=True, read_only=True)

    class Meta:
        fields = (
            'id', 'author', 'name', 'image',
            'text', 'ingredients',
            'tags', 'cooking_time',
            'is_favorited', 'is_in_shopping_cart'
            )
        model = Recipe

    def validate(self, data):
        if data.get('cooking_time') < 1:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше нуля')
        for ingredient in data.get('amount'):
            if ingredient.get('amount') < 1:
                raise serializers.ValidationError(
                    'Количество ингредиентов должно быть больше нуля'
                )    
        return data

    def image_url(self, obj):
        return f'{MEDIA_URL}{obj.image}'

    def is_favorite(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return Favorite.objects.filter(recipe=obj, user=user).exists()

    def shopping_cart(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return Shopping_cart.objects.filter(recipe=obj, user=user).exists()


class PostRecipesSerializer(GetRecipesSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all())
    ingredients = IngredientRecipeSerializer(source='amount', many=True)
    image = Base64ImageField()

    class Meta:
        fields = (
            'id', 'author', 'name', 'image',
            'text', 'ingredients',
            'tags', 'cooking_time'
            )
        model = Recipe
        validators = ()

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('amount')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            TagRecipe.objects.create(tag=tag, recipe=recipe)
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                ingredient=ingredient['id'],
                amount=ingredient['amount'],
                recipe=recipe)
        return recipe

    @transaction.atomic
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
            RecipeIngredient.objects.create(
                ingredient=ingredient['id'],
                amount=ingredient['amount'],
                recipe=instance)
        return instance


class FavoriteSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='recipe.name')
    image = serializers.ImageField(source='recipe.image')
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Favorite
        validators = (UniqueTogetherValidator(
            queryset=Favorite.objects.all(),
            fields=('recipe', 'user'),
        ),)


class SubscribeRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe


class SubscribeSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField(method_name='recipes_data')
    recipes_count = serializers.SerializerMethodField(method_name='recipes_amount')

    class Meta:
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')
        model = Subscribe

    def get_is_subscribed(self, obj):
        return Subscribe.objects.filter(
            author=obj.author, follower=obj.follower).exists()

    def recipes_amount(self, obj):
        return obj.author.recipes.all().count()

    def recipes_data(self, obj):
        recipes = Recipe.objects.filter(author=obj.author)[:3]
        serializer = SubscribeRecipeSerializer(recipes, many=True)
        return serializer.data
