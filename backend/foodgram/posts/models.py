from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Tags(models.Model):
    name = models.CharField(
        unique=True,
        max_length=200,
        )
    color = models.CharField(
        unique=True,
        max_length=7,
    )
    slug = models.SlugField(
        unique=True,
        max_length=200,
    )


class Ingredients(models.Model):
    name = models.CharField(
        max_length=200,
    )
    measurement_unit = models.CharField(
        max_length=200,
    )


class Recipes(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe'
    )
    name = models.CharField(
        max_length=200,
    )
    image = models.ImageField(upload_to='recipes/images/')
    text = models.TextField()
    ingredients = models.ManyToManyField(Ingredients, through='RecipeIngredient')
    tags = models.ManyToManyField(Tags, through='TagRecipe')
    cooking_time = models.PositiveIntegerField()


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(Ingredients, on_delete=models.CASCADE, related_name='amount')
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE, related_name='amount')
    amount = models.PositiveSmallIntegerField()


class TagRecipe(models.Model):
    tag = models.ForeignKey(Tags, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE)
