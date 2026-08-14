from django.conf import settings
from django.db import models


class Review(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = (
        (STATUS_PENDING, 'Moderatsiya kutilmoqda'),
        (STATUS_APPROVED, 'Tasdiqlangan (Ko‘rinadi)'),
        (STATUS_REJECTED, 'Rad etilgan'),
    )

    location = models.ForeignKey(
        'locations.Location',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Ishlash joyi'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Foydalanuvchi'
    )
    rating = models.PositiveSmallIntegerField(
        default=5,
        verbose_name='Umumiy baho (1-5)'
    )
    title = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Sarlavha'
    )
    text = models.TextField(verbose_name='Sharh matni')
    image = models.ImageField(
        upload_to='reviews/',
        null=True,
        blank=True,
        verbose_name='Rasm / Isbot'
    )
    
    moderation_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_APPROVED,
        verbose_name='Moderatsiya holati'
    )
    is_verified_visitor = models.BooleanField(
        default=False,
        verbose_name='Tasdiqlangan tashrifchi'
    )
    
    noise_rating = models.PositiveSmallIntegerField(default=5, verbose_name='Shovqin qulayligi (1-5)')
    wifi_rating = models.PositiveSmallIntegerField(default=5, verbose_name='Internet qulayligi (1-5)')
    comfort_rating = models.PositiveSmallIntegerField(default=5, verbose_name='Stol/rozetka qulayligi (1-5)')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Yozilgan vaqt')

    class Meta:
        verbose_name = 'Sharh va Baho'
        verbose_name_plural = 'Sharhlar va Baholar'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} → {self.location.name} ({self.rating}★)"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Recalculate average rating for location
        reviews = Review.objects.filter(location=self.location, moderation_status=self.STATUS_APPROVED)
        if reviews.exists():
            avg_r = sum(r.rating for r in reviews) / reviews.count()
            self.location.rating = round(avg_r, 1)
            self.location.review_count = reviews.count()
            self.location.save(update_fields=['rating', 'review_count'])

        # Gamification reward: +20 points for photo review, +10 for text review
        if is_new and self.user:
            pts = 20 if self.image else 10
            self.user.add_points(
                pts,
                f"{self.location.name} joyiga sharh yozildi (+{pts} ball)",
                transaction_type='photo_review' if self.image else 'review'
            )
