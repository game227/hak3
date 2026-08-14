from django.conf import settings
from django.db import models
from django.utils import timezone
from datetime import timedelta


class InternetTest(models.Model):
    SOURCE_CHOICES = (
        ('platform_speedtest', 'Sayt orqali Speedtest'),
        ('user_submission', 'Foydalanuvchi skrinshot/kiritmasi'),
        ('admin_verified', 'Admin/Ekspert tekshiruvi'),
    )

    FRESHNESS_CHOICES = (
        ('fresh', 'Yangi (< 7 kun)'),
        ('stale', 'Eskirgan (> 30 kun)'),
        ('needs_verification', 'Qayta tasdiqlanishi kerak'),
    )

    location = models.ForeignKey(
        'locations.Location',
        on_delete=models.CASCADE,
        related_name='internet_tests',
        verbose_name='Joy'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='internet_tests',
        verbose_name='Foydalanuvchi'
    )
    download_mbps = models.FloatField(verbose_name='Download tezligi (Mbps)')
    upload_mbps = models.FloatField(verbose_name='Upload tezligi (Mbps)')
    ping_ms = models.IntegerField(default=10, verbose_name='Ping (ms)')
    source = models.CharField(max_length=30, choices=SOURCE_CHOICES, default='platform_speedtest', verbose_name='Manba')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP manzil')
    device_info = models.CharField(max_length=200, blank=True, verbose_name='Qurilma ma’lumoti')
    is_verified = models.BooleanField(default=True, verbose_name='Tasdiqlangan')
    freshness_status = models.CharField(max_length=30, choices=FRESHNESS_CHOICES, default='fresh', verbose_name='Yangilik statusi')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='O‘lchov vaqti')

    class Meta:
        verbose_name = 'Internet tezlik testi'
        verbose_name_plural = 'Internet tezlik testlari'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.location.name}: {self.download_mbps} Mbps ({self.created_at.strftime('%d.%m.%Y')})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Recalculate average for location
        tests = InternetTest.objects.filter(location=self.location, is_verified=True).order_by('-created_at')[:10]
        if tests.exists():
            avg_dl = sum(t.download_mbps for t in tests) / len(tests)
            avg_ul = sum(t.upload_mbps for t in tests) / len(tests)
            avg_ping = int(sum(t.ping_ms for t in tests) / len(tests))
            self.location.avg_download_mbps = round(avg_dl, 1)
            self.location.avg_upload_mbps = round(avg_ul, 1)
            self.location.avg_ping_ms = avg_ping
            self.location.save(update_fields=['avg_download_mbps', 'avg_upload_mbps', 'avg_ping_ms'])


class NoiseTest(models.Model):
    SOURCE_CHOICES = (
        ('decibel_meter', 'Mikrofon / O‘lchagich (Web Audio)'),
        ('user_measurement', 'Foydalanuvchi qaydnomasi'),
        ('verified_sensor', 'Statsionar sensor'),
    )

    FRESHNESS_CHOICES = (
        ('fresh', 'Yangi (< 3 kun)'),
        ('stale', 'Eskirgan'),
        ('needs_verification', 'Tekshirilishi kerak'),
    )

    location = models.ForeignKey(
        'locations.Location',
        on_delete=models.CASCADE,
        related_name='noise_tests',
        verbose_name='Joy'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='noise_tests',
        verbose_name='Foydalanuvchi'
    )
    db_level = models.FloatField(verbose_name='Shovqin darajasi (dB)')
    duration_seconds = models.PositiveIntegerField(default=10, verbose_name='O‘lchov davomiyligi (soniya)')
    source = models.CharField(max_length=30, choices=SOURCE_CHOICES, default='decibel_meter', verbose_name='Manba')
    is_verified = models.BooleanField(default=True, verbose_name='Tasdiqlangan')
    freshness_status = models.CharField(max_length=30, choices=FRESHNESS_CHOICES, default='fresh', verbose_name='Yangilik statusi')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='O‘lchov vaqti')

    class Meta:
        verbose_name = 'Shovqin darajasi testi'
        verbose_name_plural = 'Shovqin testlari'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.location.name}: {self.db_level} dB ({self.created_at.strftime('%d.%m.%Y')})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update current db level for location
        recent_noise = NoiseTest.objects.filter(location=self.location, is_verified=True).order_by('-created_at')[:5]
        if recent_noise.exists():
            avg_db = sum(t.db_level for t in recent_noise) / len(recent_noise)
            self.location.current_db_level = round(avg_db, 1)
            self.location.save(update_fields=['current_db_level'])
