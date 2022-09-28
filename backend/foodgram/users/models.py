from django.contrib.auth.models import AbstractUser
from django.db import models

ADMIN_ROLE = 'admin'

class User(AbstractUser):
    email = models.EmailField(
        unique=True, max_length=254,
        verbose_name='Электронная почта',
        help_text='Введите электронную почту'
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя',
        help_text='Введите имя'
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия',
        help_text='Введите фамилию'
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        result = []
        for group in self.groups.all():
            result.append(group.name)
        return ADMIN_ROLE in result