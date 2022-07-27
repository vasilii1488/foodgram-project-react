from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


class CustomUserAdmin(UserAdmin):

    model = CustomUser
    list_display = ('id', 'username', 'first_name', 'last_name',
                    'email', 'password', 'is_staff', 'is_active',)
    ordering = ('email',)
    search_fields = ('username', 'email',)
    ordering = ('email',)


admin.site.register(CustomUser, CustomUserAdmin)
