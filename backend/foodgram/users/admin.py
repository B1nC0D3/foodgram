from django.contrib import admin
from users.models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email')
    list_filter = ('email', 'username')

admin.site.register(User, UserAdmin)

