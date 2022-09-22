from rest_framework import serializers
from posts.models import Recipe, Ingredient, Tag, RecipeIngredient, TagRecipe, Favorite, Subscribe, Shopping_cart
import base64
from django.core.files.base import ContentFile
from users.serializers import CustomUserSerializer
from foodgram.settings import MEDIA_URL
from django.contrib.auth import get_user_model

User = get_user_model()

class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    class Meta:
        
        fields = ('id', 'amount')
        model = RecipeIngredient



class GETIngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

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


class GETRecipesSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = CustomUserSerializer(read_only=True)
    image = serializers.SerializerMethodField()
    ingredients = GETIngredientRecipeSerializer(source='amount', many=True)
    tags = TagsSerializer(many=True, read_only=True)
    class Meta:
        fields = (
            'id', 'author', 'name', 'image',
            'text', 'ingredients',
            'tags', 'cooking_time', 
            'is_favorited', 'is_in_shopping_cart'
            )
        model = Recipe

    def get_image(self, obj):
        return f'{MEDIA_URL}{obj.image}'

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return Favorite.objects.filter(recipe=obj, user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return Shopping_cart.objects.filter(recipe=obj, user=user).exists()

class POSTRecipesSerializer(GETRecipesSerializer):
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    ingredients = IngredientRecipeSerializer(source='amount', many=True)
    image = Base64ImageField()

    class Meta:
        fields = (
            'id', 'author', 'name', 'image',
            'text', 'ingredients',
            'tags', 'cooking_time'
            )
        model = Recipe

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('amount')
        recipe = Recipe.objects.create(**validated_data)
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



class FavoriteSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='recipe.name')
    image = serializers.ImageField(source='recipe.image')
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')
    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Favorite


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
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        fields = ('email', 'id', 'username', 
                  'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')
        model = Subscribe
    
    def get_is_subscribed(self, obj):
        return Subscribe.objects.filter(author=obj.author, follower=obj.follower).exists()

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj.author)[:3]
        serializer = SubscribeRecipeSerializer(recipes, many=True)
        return serializer.data