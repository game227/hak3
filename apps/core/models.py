from django.conf import settings
from django.db import models


class Notification(models.Model):
    TYPE_CHOICES = (
        ('booking_confirmed', 'Buyurtma tasdiqlandi'),
        ('booking_reminder', 'Tashrif yaqinlashmoqda'),
        ('payment_status', 'To‘lov holati'),
        ('quietpass_status', 'QuietPass obunasi'),
        ('promo', 'Aksiya va Taklif'),
        ('system', 'Tizim xabari'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Foydalanuvchi'
    )
    title = models.CharField(max_length=200, verbose_name='Sarlavha')
    message = models.TextField(verbose_name='Xabar matni')
    notification_type = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES,
        default='system',
        verbose_name='Turi'
    )
    is_read = models.BooleanField(default=False, verbose_name='O‘qildi')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Yuborilgan vaqt')

    class Meta:
        verbose_name = 'Bildirishnoma'
        verbose_name_plural = 'Bildirishnomalar'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.title}"


class AuditLog(models.Model):
    ACTION_CHOICES = (
        ('payment_accept', 'To‘lov qabul qilindi & xizmat faollashtirildi'),
        ('payment_reject', 'To‘lov rad etildi'),
        ('manual_subscription_activate', 'Qo‘lda obuna/xizmat faollashtirildi'),
        ('location_approve', 'Yangi joy tasdiqlandi'),
        ('review_moderate', 'Sharh moderatsiyasi'),
        ('user_role_change', 'Foydalanuvchi roli o‘zgartirildi'),
        ('anti_fraud_ban', 'Anti-fraud cheklovi qo‘yildi'),
    )

    admin_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        verbose_name='Mas’ul Admin'
    )
    action = models.CharField(max_length=50, choices=ACTION_CHOICES, verbose_name='Bajarilgan amal')
    target_model = models.CharField(max_length=50, verbose_name='Obyekt turi')
    target_id = models.CharField(max_length=50, verbose_name='Obyekt ID')
    details = models.TextField(verbose_name='Batafsil ma’lumot va sabab')
    ip_address = models.CharField(max_length=50, blank=True, verbose_name='IP manzil')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Bajarilgan vaqt')

    class Meta:
        verbose_name = 'Audit jurnali (Audit Log)'
        verbose_name_plural = 'Audit jurnallari'
        ordering = ['-created_at']

    def __str__(self):
        admin_name = self.admin_user.username if self.admin_user else 'System'
        return f"[{self.created_at.strftime('%d.%m.%Y %H:%M')}] {admin_name} → {self.get_action_display()}"
