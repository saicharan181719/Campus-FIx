from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
    ('Campus Fix Information', {
        'fields': ('role', 'specialization'),
    }),
)

    add_fieldsets = UserAdmin.add_fieldsets + (
    ('Campus Fix Information', {
        'fields': ('role', 'specialization'),
    }),
)

    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'role',
        'specialization',
        'is_active',
        'is_staff',
    )

    list_filter = (
        'role',
        'is_active',
        'is_staff',
    )