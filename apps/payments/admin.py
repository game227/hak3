from django.contrib import admin
from .models import QuietPassPlan, Payment, QuietPass, SubscriptionRequest, ContactChannel


@admin.register(QuietPassPlan)
class QuietPassPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'plan_code', 'price', 'duration_days', 'discount_percent', 'free_beverage_daily', 'is_popular', 'is_active')
    list_filter = ('is_active', 'is_popular')
    list_editable = ('price', 'is_active')


@admin.register(ContactChannel)
class ContactChannelAdmin(admin.ModelAdmin):
    list_display = ('label', 'channel_type', 'value', 'url', 'order', 'is_active')
    list_filter = ('channel_type', 'is_active')
    list_editable = ('order', 'is_active')


@admin.register(SubscriptionRequest)
class SubscriptionRequestAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'telegram', 'plan', 'plan_days', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'plan')
    search_fields = ('full_name', 'phone', 'telegram', 'note')
    actions = ['mark_as_done', 'mark_as_rejected']

    def mark_as_done(self, request, queryset):
        for req in queryset:
            req.status = SubscriptionRequest.Status.DONE
            req.save(update_fields=['status'])
            # Also accept linked payment if exists
            payment = Payment.objects.filter(subscription_request=req).first()
            if payment:
                payment.accept_payment(request.user, note="Admin panel orqali so‘rov tasdiqlandi")
        self.message_user(request, f"{queryset.count()} ta so‘rov tasdiqlandi va obuna faollashtirildi.")
    mark_as_done.short_description = "Tanlangan so‘rovlarni TASDIQLASH va OBUNA BERISH"

    def mark_as_rejected(self, request, queryset):
        queryset.update(status=SubscriptionRequest.Status.REJECTED)
        self.message_user(request, "Tanlangan so‘rovlar rad etildi.")
    mark_as_rejected.short_description = "Tanlangan so‘rovlarni RAD ETISH"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'amount', 'provider', 'payment_type', 'status', 'processed_by', 'created_at')
    list_filter = ('status', 'provider', 'payment_type', 'created_at')
    search_fields = ('transaction_id', 'user__username', 'admin_note')
    readonly_fields = ('transaction_id', 'created_at')
    actions = ['mark_as_accepted', 'mark_as_rejected']

    def mark_as_accepted(self, request, queryset):
        for p in queryset:
            p.accept_payment(request.user, note="Admin panel orqali ommaviy tasdiqlandi.")
        self.message_user(request, f"{queryset.count()} ta to‘lov muvaffaqiyatli qabul qilindi va tegishli xizmatlar faollashtirildi.")
    mark_as_accepted.short_description = "Tanlangan to‘lovlarni QABUL QILISH (Accept & Activate)"

    def mark_as_rejected(self, request, queryset):
        for p in queryset:
            p.reject_payment(request.user, reason="Admin panel orqali rad etildi.")
        self.message_user(request, f"{queryset.count()} ta to‘lov rad etildi.")
    mark_as_rejected.short_description = "Tanlangan to‘lovlarni RAD ETISH (Reject)"


@admin.register(QuietPass)
class QuietPassAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan_name', 'price', 'status', 'start_date', 'end_date', 'created_at')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('user__username', 'plan_name')
