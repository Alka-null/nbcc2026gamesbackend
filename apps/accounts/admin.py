from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Player


@admin.register(Player)
class PlayerAdmin(UserAdmin):
    model = Player
    list_display = ('id', 'name', 'email', 'unique_code', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('email', 'name', 'unique_code')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {'fields': ('email', 'password', 'name', 'unique_code', 'organization')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2', 'is_staff', 'is_superuser'),
        }),
    )

    readonly_fields = ('unique_code',)
