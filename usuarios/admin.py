# usuarios/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'user_type',
        'is_staff',
    )

    # Campos exibidos ao editar um usuário
    fieldsets = UserAdmin.fieldsets + (('User Type', {'fields': ('user_type',)}),)

    # Campos exibidos ao criar um usuário (incluindo superusuário)
    add_fieldsets = UserAdmin.add_fieldsets + (('User Type', {'fields': ('user_type',)}),)


admin.site.register(CustomUser, CustomUserAdmin)
