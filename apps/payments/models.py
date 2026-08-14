import uuid
from datetime import timedelta
from django.conf import settings
from django.db import models
from django.utils import timezone


def generate_tx_id():
    return f"TX-{uuid.uuid4().hex[:10].upper()}"


class QuietPassPlan(models.Model):
    name = models.CharField(max_length=100, verbose_name='Reja nomi')
    plan_code = models.CharField(max_length=30, unique=True, verbose_name='Kod')
    price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='Narxi (so‘m)')
    duration_days = models.PositiveIntegerField(default=30, verbose_name='Amal qilish muddati (kun)')
    discount_percent = models.PositiveIntegerField(default=15, verbose_name='Hamkor joylarda chegirma (%)')
    free_beverage_daily = models.BooleanField(default=True, verbose_name='Kunlik 1 ta bepul kofe/choy')
    description = models.TextField(blank=True, verbose_name='Tavsif')
    is_popular = models.BooleanField(default=False, verbose_name='Tavsiya etiladi')
    order = models.PositiveIntegerField(default=0, verbose_name='Tartib')
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'QuietPass Rejasi'
        verbose_name_plural = 'QuietPass Rejalari'
        ordering = ['order', 'price']

    def __str__(self):
        return f"{self.name} — {self.price:,.0f} so‘m / {self.duration_days} kun"

    @property
    def price_label(self):
        return f"{self.price:,.0f}".replace(',', ' ') + " so‘m"


class ContactChannel(models.Model):
    class ChannelType(models.TextChoices):
        PHONE = 'PHONE', 'Telefon'
        EMAIL = 'EMAIL', 'Email'
        TELEGRAM = 'TELEGRAM', 'Telegram'
        INSTAGRAM = 'INSTAGRAM', 'Instagram'
        OTHER = 'OTHER', 'Boshqa'

    label = models.CharField(max_length=80, verbose_name='Sarlavha')
    channel_type = models.CharField(
        max_length=20, choices=ChannelType.choices, default=ChannelType.TELEGRAM,
        verbose_name='Turi'
    )
    value = models.CharField(
        max_length=255, verbose_name='Qiymat',
        help_text='Masalan: +998901234567, @QuietSpaceSupport'
    )
    url = models.URLField(blank=True, verbose_name='Havola')
    icon = models.CharField(max_length=40, default='bi-telegram', verbose_name='Bootstrap Icon')
    order = models.PositiveIntegerField(default=0, verbose_name='Tartib')
    is_active = models.BooleanField(default=True, verbose_name='Faol')

    class Meta:
        verbose_name = 'Kontakt kanali'
        verbose_name_plural = 'Kontakt kanallari'
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.label}: {self.value}"

    @property
    def href(self):
        if self.url:
            return self.url
        if self.channel_type == self.ChannelType.TELEGRAM:
            handle = self.value.lstrip('@')
            return f"https://t.me/{handle}"
        if self.channel_type == self.ChannelType.PHONE:
            return f"tel:{self.value.replace(' ', '')}"
        if self.channel_type == self.ChannelType.EMAIL:
            return f"mailto:{self.value}"
        if self.channel_type == self.ChannelType.INSTAGRAM:
            handle = self.value.lstrip('@')
            return f"https://instagram.com/{handle}"
        return ''


class SubscriptionRequest(models.Model):
    class Status(models.TextChoices):
        NEW = 'NEW', 'Yangi'
        CONTACTED = 'CONTACTED', 'Bog‘lanildi'
        DONE = 'DONE', 'Tasdiqlandi / Bajarildi'
        REJECTED = 'REJECTED', 'Rad etildi'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subscription_requests',
        verbose_name='Foydalanuvchi'
    )
    full_name = models.CharField(max_length=120, verbose_name='To‘liq ism')
    phone = models.CharField(max_length=30, verbose_name='Telefon')
    telegram = models.CharField(max_length=120, blank=True, verbose_name='Telegram')
    plan = models.ForeignKey(
        QuietPassPlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Tanlangan tarif'
    )
    plan_days = models.PositiveIntegerField(default=30, verbose_name='Tarif muddati (kun)')
    amount = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name='Summa')
    receipt_image = models.ImageField(upload_to='receipts/', null=True, blank=True, verbose_name='To‘lov cheki')
    note = models.TextField(blank=True, verbose_name='Izoh / Xabar')
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        verbose_name='Holat'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Yuborilgan vaqt')

    class Meta:
        verbose_name = 'Obuna so‘rovi'
        verbose_name_plural = 'Obuna so‘rovlari'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} — {self.plan.name if self.plan else self.plan_days} ({self.get_status_display()})"


class Payment(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PAID = 'paid'
    STATUS_FAILED = 'failed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_REFUNDED = 'refunded'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = (
        (STATUS_PENDING, 'Kutilmoqda (Pending)'),
        (STATUS_PAID, 'To‘langan (Paid / Active)'),
        (STATUS_FAILED, 'Muvaffaqiyatsiz (Failed)'),
        (STATUS_CANCELLED, 'Bekor qilingan (Cancelled)'),
        (STATUS_REFUNDED, 'Qaytarilgan (Refunded)'),
        (STATUS_REJECTED, 'Rad etilgan (Rejected)'),
    )

    PROVIDER_CHOICES = (
        ('click', 'Click Up'),
        ('payme', 'Payme'),
        ('uzum', 'Uzum Bank'),
        ('manual_transfer', 'Karta / Manual chek yuklash'),
        ('cash', 'Joyida naqd / Karta'),
    )

    TYPE_CHOICES = (
        ('booking', 'Stol / Zona bron qilish'),
        ('quietpass', 'QuietPass obunasi'),
        ('promoted_listing', 'B2B Reklama / Promoted Listing'),
    )

    transaction_id = models.CharField(
        max_length=50,
        unique=True,
        default=generate_tx_id,
        verbose_name='Tranzaksiya ID'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='Foydalanuvchi'
    )
    booking = models.ForeignKey(
        'bookings.Booking',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
        verbose_name='Bog‘langan Booking'
    )
    quietpass = models.ForeignKey(
        'QuietPass',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
        verbose_name='Bog‘langan QuietPass'
    )
    subscription_request = models.ForeignKey(
        SubscriptionRequest,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
        verbose_name='Bog‘langan so‘rov'
    )
    payment_type = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES,
        default='booking',
        verbose_name='To‘lov turi'
    )
    provider = models.CharField(
        max_length=30,
        choices=PROVIDER_CHOICES,
        default='manual_transfer',
        verbose_name='To‘lov provayderi'
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name='Summa (so‘m)'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name='To‘lov holati'
    )
    receipt_image = models.ImageField(
        upload_to='receipts/',
        null=True,
        blank=True,
        verbose_name='To‘lov cheki / Skrinshot'
    )
    admin_note = models.TextField(
        blank=True,
        verbose_name='Admin izohi / Rad etish sababi'
    )
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_payments',
        verbose_name='Tekshirgan Admin'
    )
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name='Tekshirilgan vaqt')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan vaqt')

    class Meta:
        verbose_name = 'To‘lov (Payment)'
        verbose_name_plural = 'To‘lovlar (Payments)'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_id} | {self.user.username} | {self.amount:,.0f} UZS ({self.get_status_display()})"

    def accept_payment(self, admin_user, note=''):
        from apps.core.models import AuditLog, Notification
        self.status = self.STATUS_PAID
        self.processed_by = admin_user
        self.processed_at = timezone.now()
        if note:
            self.admin_note = note
        self.save(update_fields=['status', 'processed_by', 'processed_at', 'admin_note'])

        if self.subscription_request:
            self.subscription_request.status = SubscriptionRequest.Status.DONE
            self.subscription_request.save(update_fields=['status'])

        # Activate associated booking or quietpass
        if self.booking:
            self.booking.status = 'confirmed'
            self.booking.save(update_fields=['status'])
            Notification.objects.create(
                user=self.user,
                title='To‘lov tasdiqlandi!',
                message=f"{self.booking.location.name} joyidagi buyurtmangiz (#{self.booking.booking_code}) tasdiqlandi.",
                notification_type='payment_status'
            )

        if self.quietpass:
            self.quietpass.status = 'active'
            self.quietpass.start_date = timezone.now().date()
            duration = self.quietpass.plan.duration_days if self.quietpass.plan else 30
            self.quietpass.end_date = timezone.now().date() + timedelta(days=duration)
            self.quietpass.save(update_fields=['status', 'start_date', 'end_date'])
            Notification.objects.create(
                user=self.user,
                title='QuietPass faollashtirildi!',
                message=f"Sizning {self.quietpass.plan_name} obunangiz muvaffaqiyatli faollashtirildi. Amal qilish muddati: {self.quietpass.end_date} gacha.",
                notification_type='quietpass_status'
            )

        AuditLog.objects.create(
            admin_user=admin_user,
            action='payment_accept',
            target_model='Payment',
            target_id=str(self.id),
            details=f"To‘lov qabul qilindi. Summa: {self.amount} UZS. Tranzaksiya: {self.transaction_id}."
        )

    def reject_payment(self, admin_user, reason=''):
        from apps.core.models import AuditLog, Notification
        self.status = self.STATUS_REJECTED
        self.processed_by = admin_user
        self.processed_at = timezone.now()
        self.admin_note = reason
        self.save(update_fields=['status', 'processed_by', 'processed_at', 'admin_note'])

        if self.subscription_request:
            self.subscription_request.status = SubscriptionRequest.Status.REJECTED
            self.subscription_request.save(update_fields=['status'])

        if self.quietpass:
            self.quietpass.status = 'cancelled'
            self.quietpass.save(update_fields=['status'])

        Notification.objects.create(
            user=self.user,
            title='To‘lov rad etildi',
            message=f"To‘lovingiz (#{self.transaction_id}) rad etildi. Sabab: {reason or 'Tekshiruvdan o‘tmadi'}",
            notification_type='payment_status'
        )

        AuditLog.objects.create(
            admin_user=admin_user,
            action='payment_reject',
            target_model='Payment',
            target_id=str(self.id),
            details=f"To‘lov rad etildi. Sabab: {reason}. Tranzaksiya: {self.transaction_id}."
        )


class QuietPass(models.Model):
    STATUS_CHOICES = (
        ('inactive', 'Nofaol'),
        ('pending', 'Tasdiqlash kutilmoqda'),
        ('active', 'Faol (Active)'),
        ('expired', 'Muddati tugagan'),
        ('cancelled', 'Bekor qilingan'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quietpasses',
        verbose_name='Foydalanuvchi'
    )
    plan = models.ForeignKey(
        QuietPassPlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Tanlangan reja'
    )
    plan_name = models.CharField(max_length=100, default='Oylik Pass', verbose_name='Reja nomi')
    price = models.DecimalField(max_digits=12, decimal_places=0, default=290000, verbose_name='To‘langan summa')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Holati')
    
    start_date = models.DateField(null=True, blank=True, verbose_name='Boshlanish sanasi')
    end_date = models.DateField(null=True, blank=True, verbose_name='Tugash sanasi')
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'QuietPass Obunasi'
        verbose_name_plural = 'QuietPass Obunalari'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} — {self.plan_name} ({self.get_status_display()})"

    @property
    def is_currently_active(self):
        if self.status == 'active' and self.end_date and self.end_date >= timezone.now().date():
            return True
        return False
