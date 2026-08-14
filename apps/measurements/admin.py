from django.contrib import admin
from .models import InternetTest, NoiseTest


@admin.register(InternetTest)
class InternetTestAdmin(admin.ModelAdmin):
    list_display = ('location', 'download_mbps', 'upload_mbps', 'ping_ms', 'source', 'user', 'freshness_status', 'is_verified', 'created_at')
    list_filter = ('source', 'freshness_status', 'is_verified')
    search_fields = ('location__name', 'user__username', 'ip_address')


@admin.register(NoiseTest)
class NoiseTestAdmin(admin.ModelAdmin):
    list_display = ('location', 'db_level', 'duration_seconds', 'source', 'user', 'freshness_status', 'is_verified', 'created_at')
    list_filter = ('source', 'freshness_status', 'is_verified')
    search_fields = ('location__name', 'user__username')
