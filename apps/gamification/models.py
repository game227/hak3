from django.conf import settings
from django.db import models


class RewardTransaction(models.Model):
    TYPE_CHOICES = (
        ('speedtest', 'Speedtest o‘tkazish (+10)'),
        ('new_location', 'Yangi joy qo‘shish (+50)'),
        ('photo_review', 'Foto/video sharh yozish (+20)'),
        ('review', 'Oddiy sharh (+10)'),
        ('quietpass_discount', 'QuietPass uchun sarflash (-ball)'),
        ('free_coffee_redeem', 'Bepul kofe kuponi (-ball)'),
        ('admin_grant', 'Admin tomonidan berildi'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reward_transactions',
        verbose_name='Foydalanuvchi'
    )
    points = models.IntegerField(verbose_name='Ball miqdori (+/-)')
    transaction_type = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES,
        default='speedtest',
        verbose_name='Amal turi'
    )
    description = models.CharField(max_length=255, verbose_name='Tavsif')
    is_anti_fraud_flagged = models.BooleanField(default=False, verbose_name='Shubhali / Tekshirilmoqda')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Sana va vaqt')

    class Meta:
        verbose_name = 'Ballar amaliyoti'
        verbose_name_plural = 'Ballar amaliyotlari'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.points:+d} ({self.get_transaction_type_display()})"


class Promotion(models.Model):
    location = models.ForeignKey(
        'locations.Location',
        on_delete=models.CASCADE,
        related_name='promotions',
        verbose_name='Joy'
    )
    title = models.CharField(max_length=150, verbose_name='Aksiya sarlavhasi')
    description = models.TextField(verbose_name='Batafsil shartlar')
    discount_percent = models.PositiveIntegerField(default=10, verbose_name='Chegirma foizi (%)')
    start_date = models.DateField(verbose_name='Boshlanish sanasi')
    end_date = models.DateField(verbose_name='Tugash sanasi')
    is_active = models.BooleanField(default=True, verbose_name='Faol')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Aksiya va Taklif (Promotion)'
        verbose_name_plural = 'Aksiyalar va Takliflar'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.location.name} — {self.title} (-{self.discount_percent}%)"
