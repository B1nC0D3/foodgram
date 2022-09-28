from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from foodgram import settings

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        unique=True,
        max_length=200,
        verbose_name='Наименование тэга',
        help_text='Введите наименование тэга'
        )
    color = models.CharField(
        unique=True,
        max_length=7,
        verbose_name='Цвет тэга',
        help_text='Введите Цвет тэга'
    )
    slug = models.SlugField(
        unique=True,
        max_length=200,
        verbose_name='Слаг тэга',
        help_text='Введите слаг тэга'
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Наименование ингредиента',
        help_text='Введите наименование ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Мера измерения',
        help_text='Введите меру измерения'
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
        help_text='Выберите автора рецепта'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Наименование рецепта',
        help_text='Введите наименование рецепта'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Картинка рецепта',
        help_text='Выберите файл'
    )
    text = models.TextField(
        verbose_name='Описание рецепта', 
        help_text='Введите описание')
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient',
        verbose_name='Ингредиенты в рецепте',
        help_text='Выберите ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag, through='TagRecipe',
        verbose_name='Тэги рецепта',
        help_text='Выберите тэги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(settings.COOKING_TIME_MIN),),
        verbose_name='Время приготовления',
        help_text=f'Введите время приготовления, больше {settings.COOKING_TIME_MIN}'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self) -> str:
        return self.name


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, 
        related_name='amount',
        verbose_name='Ингредиенты в рецепте',
        help_text='Выберите ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, 
        related_name='amount',
        verbose_name='Рецепт ингредиента',
        help_text='Выберите рецепт'
    )
    amount = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(settings.AMOUNT_MIN),),
        verbose_name='Количество ингредиентов',
        help_text=f'Введите число, больше {settings.AMOUNT_MIN}'
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Ингредиенты'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self) -> str:
        return f'{self.ingredient} принадлежащий {self.recipe}'


class TagRecipe(models.Model):
    tag = models.ForeignKey(
        Tag, on_delete=models.CASCADE, 
        related_name='recipe_tag',
        verbose_name='Тэги рецепта',
        help_text='Выберите тэг'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        verbose_name='Рецепты тэгов',
        help_text='Выберите рецепт'
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Тэги'
        verbose_name_plural = 'Тэги'

    def __str__(self) -> str:
        return f'{self.tag} принадлежащий {self.recipe}'


class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, 
        related_name='recipes',
        verbose_name='Избранный рецепт',
        help_text='Выберите рецепт'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, 
        related_name='user',
        verbose_name='Подписчик',
        help_text='Выберите человека'
    )

    class Meta:
        unique_together = ('recipe', 'user')
        ordering = ('id',)
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self) -> str:
        return f'{self.recipe} в избранном у {self.user}'
        

class Subscribe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, 
        related_name='author',
        verbose_name='Автор',
        help_text='Выберите человека'
    )
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, 
        related_name='follower',
        verbose_name='Подписчик',
        help_text='Выберите человека'
    )

    class Meta:
        unique_together = ('author', 'follower')
        ordering = ('id',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self) -> str:
        return f'{self.follower} подписан на {self.author}'

class Shopping_cart(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, 
        related_name='shop_recipe',
        verbose_name='Рецепт в корзине',
        help_text='Выберите рецепт'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, 
        related_name='shop_user',
        verbose_name='Пользователь корзины',
        help_text='Выберите человека'
        )

    class Meta:
        unique_together = ('recipe', 'user')
        ordering = ('id',)
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'
    
    def __str__(self) -> str:
        return f'{self.recipe} в корзине у {self.user}'
