from django.contrib import admin
from users.models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'username', 'email', 'first_name', 'role')
    empty_value_display = '-пусто-'
    list_editable = ('username', 'role',)


admin.site.register(User, UserAdmin)
