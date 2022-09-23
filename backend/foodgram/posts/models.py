from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
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

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
    )
    measurement_unit = models.CharField(
        max_length=200,
    )

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
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
    ingredients = models.ManyToManyField(Ingredient, through='RecipeIngredient')
    tags = models.ManyToManyField(Tag, through='TagRecipe')
    cooking_time = models.PositiveIntegerField()

    def __str__(self) -> str:
        return self.name


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='amount')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='amount')
    amount = models.PositiveSmallIntegerField()


class TagRecipe(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='recipe_tag')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)


class Favorite(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipe')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')

    class Meta:
        unique_together = ('recipe', 'user')


class Subscribe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author')
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower')

    class Meta:
        unique_together = ('author', 'follower')


class Shopping_cart(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='shop_recipe')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shop_user')

    class Meta:
        unique_together = ('recipe', 'user')