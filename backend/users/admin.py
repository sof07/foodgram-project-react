from django.contrib import admin
from users.models import CustomUser
class CustomUsersAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')
    search_fields = ('email', 'username')


admin.site.register(CustomUser, CustomUsersAdmin)
