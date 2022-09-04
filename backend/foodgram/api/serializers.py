from rest_framework import serializers
from posts.models import Recipes


class RecipesSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'author', 'name', 'pic',
            'description', 'ingredients',
            'tag', 'cooking_time'
            )
        model = Recipes
