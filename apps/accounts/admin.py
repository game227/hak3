from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'status_tier', 'points', 'telegram_id', 'is_staff')
    list_filter = ('role', 'status_tier', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone_number', 'telegram_username')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('QuietSpace Qo‘shimcha Ma’lumotlar', {
            'fields': ('role', 'phone_number', 'telegram_id', 'telegram_username', 'points', 'status_tier', 'avatar', 'bio')
        }),
    )
