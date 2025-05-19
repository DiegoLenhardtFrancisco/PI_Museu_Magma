# usuarios/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'tipo_usuario', 'is_staff')
    
    # Campos exibidos ao editar um usuário
    fieldsets = UserAdmin.fieldsets + (
        ('Tipo de Usuário', {'fields': ('tipo_usuario',)}),
    )
    
    # Campos exibidos ao criar um usuário (incluindo superusuário)
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Tipo de Usuário', {'fields': ('tipo_usuario',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)