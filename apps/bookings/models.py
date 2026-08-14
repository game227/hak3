import random
import string
from django.conf import settings
from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.utils import timezone


def generate_booking_code():
    return 'QS-' + ''.join(random.choices(string.digits, k=6))


class Booking(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_CHECKED_IN = 'checked_in'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = (
        (STATUS_PENDING, 'To‘lov kutilmoqda (Pending)'),
        (STATUS_CONFIRMED, 'Tasdiqlangan (Confirmed)'),
        (STATUS_CHECKED_IN, 'Mijoz kelgan (Checked In)'),
        (STATUS_COMPLETED, 'Tugallangan (Completed)'),
        (STATUS_CANCELLED, 'Bekor qilingan (Cancelled)'),
    )

    booking_code = models.CharField(
        max_length=20,
        unique=True,
        default=generate_booking_code,
        verbose_name='Buyurtma kodi'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name='Foydalanuvchi'
    )
    location = models.ForeignKey(
        'locations.Location',
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name='Ishlash joyi'
    )
    zone = models.ForeignKey(
        'locations.Zone',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bookings',
        verbose_name='Zona'
    )
    table = models.ForeignKey(
        'locations.TableDesk',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bookings',
        verbose_name='Stol / Joy'
    )

    booking_date = models.DateField(verbose_name='Sana')
    start_time = models.TimeField(verbose_name='Boshlanish vaqti')
    end_time = models.TimeField(verbose_name='Tugash vaqti')
    total_hours = models.DecimalField(max_digits=4, decimal_places=1, default=1.0, verbose_name='Davomiyligi (soat)')

    price_per_hour = models.DecimalField(max_digits=10, decimal_places=0, default=20000, verbose_name='1 soatlik narx')
    total_price = models.DecimalField(max_digits=12, decimal_places=0, default=20000, verbose_name='Jami summa (so‘m)')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING, verbose_name='Holati')
    cancellation_reason = models.TextField(blank=True, verbose_name='Bekor qilish sababi')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan vaqt')

    class Meta:
        verbose_name = 'Buyurtma (Booking)'
        verbose_name_plural = 'Buyurtmalar (Bookings)'
        ordering = ['-booking_date', '-start_time']

    def __str__(self):
        return f"{self.booking_code} | {self.location.name} | {self.booking_date} ({self.get_status_display()})"

    def clean(self):
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError("Tugash vaqti boshlanish vaqtidan keyin bo‘lishi shart.")

    @classmethod
    def check_conflict(cls, table, booking_date, start_time, end_time, exclude_id=None):
        if not table:
            return False
        qs = cls.objects.filter(
            table=table,
            booking_date=booking_date,
            status__in=[cls.STATUS_PENDING, cls.STATUS_CONFIRMED, cls.STATUS_CHECKED_IN]
        )
        if exclude_id:
            qs = qs.exclude(id=exclude_id)
        
        # Conflict exists if: (start_time < existing_end) AND (end_time > existing_start)
        conflict = qs.filter(start_time__lt=end_time, end_time__gt=start_time).exists()
        return conflict

    @property
    def status_badge_class(self):
        if self.status == self.STATUS_CONFIRMED:
            return 'bg-emerald-500 text-white'
        elif self.status == self.STATUS_CHECKED_IN:
            return 'bg-blue-600 text-white'
        elif self.status == self.STATUS_COMPLETED:
            return 'bg-slate-600 text-white'
        elif self.status == self.STATUS_PENDING:
            return 'bg-amber-500 text-slate-900'
        return 'bg-rose-500 text-white'


class CheckIn(models.Model):
    METHOD_CHOICES = (
        ('qr_code', 'QR-kod skanerlandi'),
        ('code_manual', 'Kodni qo‘lda kiritish'),
        ('geo_location', 'GPS Geo Check-in'),
    )

    booking = models.ForeignKey(
        Booking,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='checkins',
        verbose_name='Buyurtma'
    )
    location = models.ForeignKey(
        'locations.Location',
        on_delete=models.CASCADE,
        related_name='checkins',
        verbose_name='Joy'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='checkins',
        verbose_name='Foydalanuvchi'
    )
    check_in_code = models.CharField(max_length=50, blank=True, verbose_name='Check-in kodi')
    method = models.CharField(max_length=30, choices=METHOD_CHOICES, default='qr_code')
    is_verified = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Kelgan vaqti')

    class Meta:
        verbose_name = 'Check-in (Tashrif)'
        verbose_name_plural = 'Check-inlar'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} @ {self.location.name} ({self.created_at.strftime('%d.%m.%Y %H:%M')})"
