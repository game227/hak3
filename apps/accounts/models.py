from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_USER = 'user'
    ROLE_BUSINESS_OWNER = 'business_owner'
    ROLE_MODERATOR = 'moderator'
    ROLE_PAYMENT_ADMIN = 'payment_admin'
    ROLE_SUPERADMIN = 'superadmin'

    ROLE_CHOICES = (
        (ROLE_USER, 'Foydalanuvchi'),
        (ROLE_BUSINESS_OWNER, 'Biznes egasi'),
        (ROLE_MODERATOR, 'Moderator'),
        (ROLE_PAYMENT_ADMIN, 'To‘lov admini'),
        (ROLE_SUPERADMIN, 'Super Admin'),
    )

    TIER_EXPLORER = 'explorer'
    TIER_QUIET_MASTER = 'quiet_master'
    TIER_SPACE_GURU = 'space_guru'

    TIER_CHOICES = (
        (TIER_EXPLORER, 'Explorer (0-100 ball)'),
        (TIER_QUIET_MASTER, 'Quiet Master (101-500 ball)'),
        (TIER_SPACE_GURU, 'Space Guru (500+ ball)'),
    )

    role = models.CharField(
        max_length=30,
        choices=ROLE_CHOICES,
        default=ROLE_USER,
        verbose_name='Rol'
    )
    phone_number = models.CharField(
        max_length=25,
        blank=True,
        verbose_name='Telefon raqami'
    )
    telegram_id = models.BigIntegerField(
        null=True,
        blank=True,
        unique=True,
        verbose_name='Telegram ID'
    )
    telegram_username = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Telegram Username'
    )
    points = models.PositiveIntegerField(
        default=0,
        verbose_name='Gamifikatsiya ballari'
    )
    status_tier = models.CharField(
        max_length=30,
        choices=TIER_CHOICES,
        default=TIER_EXPLORER,
        verbose_name='Status darajasi'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        verbose_name='Profil rasmi'
    )
    bio = models.TextField(
        blank=True,
        verbose_name='O‘zi haqida'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Ro‘yxatdan o‘tgan vaqt'
    )

    class Meta:
        verbose_name = 'Foydalanuvchi'
        verbose_name_plural = 'Foydalanuvchilar'
        ordering = ['-date_joined']

    def __str__(self):
        if self.first_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.username

    def update_tier(self):
        if self.points >= 500:
            self.status_tier = self.TIER_SPACE_GURU
        elif self.points >= 101:
            self.status_tier = self.TIER_QUIET_MASTER
        else:
            self.status_tier = self.TIER_EXPLORER
        self.save(update_fields=['status_tier'])

    def add_points(self, amount: int, description: str = '', transaction_type: str = 'other'):
        from apps.gamification.models import RewardTransaction
        self.points += amount
        self.save(update_fields=['points'])
        self.update_tier()
        RewardTransaction.objects.create(
            user=self,
            points=amount,
            transaction_type=transaction_type,
            description=description
        )

    @property
    def is_business(self):
        return self.role == self.ROLE_BUSINESS_OWNER or self.is_superuser

    @property
    def is_moderator_user(self):
        return self.role in [self.ROLE_MODERATOR, self.ROLE_SUPERADMIN] or self.is_superuser

    @property
    def is_payment_admin_user(self):
        return self.role in [self.ROLE_PAYMENT_ADMIN, self.ROLE_SUPERADMIN] or self.is_superuser

    @property
    def tier_badge_color(self):
        if self.status_tier == self.TIER_SPACE_GURU:
            return 'bg-purple-600'
        if self.status_tier == self.TIER_QUIET_MASTER:
            return 'bg-blue-600'
        return 'bg-slate-500'
