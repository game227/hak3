from django.contrib import admin
from .models import RewardTransaction, Promotion


@admin.register(RewardTransaction)
class RewardTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'points', 'transaction_type', 'description', 'is_anti_fraud_flagged', 'created_at')
    list_filter = ('transaction_type', 'is_anti_fraud_flagged', 'created_at')
    search_fields = ('user__username', 'description')


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'discount_percent', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('title', 'location__name', 'description')
