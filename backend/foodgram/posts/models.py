from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tags(models.Model):
    name = models.CharField(
        unique=True,
        max_length=50,
        )
    color = models.CharField(
        unique=True,
        max_length=6,
    )
    slug = models.SlugField(
        unique=True,
    )


class Ingredients(models.Model):
    name = models.CharField(
        max_length=100,
    )
    measure = models.CharField(
        max_length=10,
    )


# class Ingredients(models.Model):
#     ingredient = models.ForeignKey(
#         Products,
#         on_delete=models.CASCADE,
#     )
#     amount = models.SmallIntegerField()


class Recipes(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe'
    )
    name = models.CharField(
        max_length=50,
    )
    pic = models.ImageField()
    description = models.TextField()
    ingredients = models.ManyToManyField(Ingredients)
    tag = models.ManyToManyField(Tags)
    cooking_time = models.IntegerField()
