from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('location', 'user', 'rating', 'moderation_status', 'is_verified_visitor', 'created_at')
    list_filter = ('rating', 'moderation_status', 'is_verified_visitor')
    search_fields = ('location__name', 'user__username', 'text', 'title')
    actions = ['approve_reviews', 'reject_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(moderation_status='approved')
        self.message_user(request, "Tanlangan sharhlar tasdiqlandi.")
    approve_reviews.short_description = "Tanlangan sharhlarni TASDIQLASH"

    def reject_reviews(self, request, queryset):
        queryset.update(moderation_status='rejected')
        self.message_user(request, "Tanlangan sharhlar rad etildi.")
    reject_reviews.short_description = "Tanlangan sharhlarni RAD ETISH"
