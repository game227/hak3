from django.contrib import admin
from .models import Notification, AuditLog


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'title', 'message')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'admin_user', 'target_model', 'target_id', 'created_at', 'ip_address')
    list_filter = ('action', 'target_model', 'created_at')
    search_fields = ('admin_user__username', 'details', 'target_id')
    readonly_fields = ('admin_user', 'action', 'target_model', 'target_id', 'details', 'ip_address', 'created_at')
