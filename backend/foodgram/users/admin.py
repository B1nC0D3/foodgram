from django.contrib import admin
from django.contrib.auth.models import Permission
from users.models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'is_admin', 'is_superuser')
    search_fields = ('email', 'username')

    def is_admin(self, obj):
        if obj.is_admin:
            return 'Да'
        return 'Нет'

admin.site.register(User, UserAdmin)
