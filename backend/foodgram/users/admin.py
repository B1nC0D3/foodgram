from django.contrib import admin
from users.models import User
from django.contrib.auth.models import Permission

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'get_group')
    list_filter = ('email', 'username')

    def get_group(self, obj):
        result = []
        for group in obj.groups.all():
            result.append(group.name)
        return result

admin.site.register(User, UserAdmin)

