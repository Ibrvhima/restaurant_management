from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['login', 'role', 'actif', 'date_creation']
    list_filter = ['role', 'actif', 'date_creation']
    search_fields = ['login']
    ordering = ['-date_creation']
    
    fieldsets = (
        (None, {'fields': ('login', 'password')}),
        ('Informations', {'fields': ('role', 'actif')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('login', 'password1', 'password2', 'role', 'actif'),
        }),
    )
    
    filter_horizontal = ('groups', 'user_permissions',)
