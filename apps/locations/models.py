from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Business(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='businesses',
        verbose_name='Biznes egasi'
    )
    name = models.CharField(max_length=200, verbose_name='Yuridik nomi')
    brand_name = models.CharField(max_length=200, verbose_name='Brend nomi')
    inn = models.CharField(max_length=20, blank=True, verbose_name='INN / STIR')
    phone = models.CharField(max_length=30, verbose_name='Bog‘lanish telefoni')
    email = models.EmailField(blank=True, verbose_name='Email')
    description = models.TextField(blank=True, verbose_name='Tavsif')
    is_verified = models.BooleanField(default=False, verbose_name='Tasdiqlangan')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan vaqt')

    class Meta:
        verbose_name = 'Biznes / Hamkor'
        verbose_name_plural = 'Bizneslar / Hamkorlar'

    def __str__(self):
        return self.brand_name or self.name


class Amenity(models.Model):
    CATEGORY_CHOICES = (
        ('connectivity', 'Aloqa va Internet'),
        ('comfort', 'Qulaylik va Muhit'),
        ('facility', 'Xizmatlar va Inshoot'),
    )

    name = models.CharField(max_length=100, verbose_name='Qulaylik nomi')
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=60, default='bi-check-circle', verbose_name='Bootstrap Icon klassi')
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='comfort')

    class Meta:
        verbose_name = 'Qulaylik (Amenity)'
        verbose_name_plural = 'Qulayliklar'
        ordering = ['name']

    def __str__(self):
        return self.name


class Location(models.Model):
    CATEGORY_COWORKING = 'coworking'
    CATEGORY_CAFE = 'cafe'
    CATEGORY_LIBRARY = 'library'
    CATEGORY_STUDY_ZONE = 'study_zone'
    CATEGORY_LOUNGE = 'lounge'

    CATEGORY_CHOICES = (
        (CATEGORY_COWORKING, 'Kovorking'),
        (CATEGORY_CAFE, 'Qahvaxona / Tinch Kafe'),
        (CATEGORY_LIBRARY, 'Kutubxona'),
        (CATEGORY_STUDY_ZONE, 'Study Zone / O‘quv markazi'),
        (CATEGORY_LOUNGE, 'Work Lounge'),
    )

    DISTRICT_CHOICES = (
        ('chorsu', 'Chorsu / Eski shahar'),
        ('shayxontohur', 'Shayxontohur'),
        ('yunusobod', 'Yunusobod'),
        ('mirzo_ulugbek', 'Mirzo Ulug‘bek'),
        ('mirobod', 'Mirobod'),
        ('yakkasaroy', 'Yakkasaroy'),
        ('chilonzor', 'Chilonzor'),
        ('uchtepa', 'Uchtepa'),
        ('sergeli', 'Sergeli'),
        ('olmazor', 'Olmazor'),
        ('yashnobod', 'Yashnobod'),
    )

    LIVE_QUIET = 'quiet'
    LIVE_MODERATE = 'moderate'
    LIVE_BUSY = 'busy'

    LIVE_STATUS_CHOICES = (
        (LIVE_QUIET, '🟢 Tinch va bo‘sh joylar ko‘p'),
        (LIVE_MODERATE, '🟡 O‘rtacha gavjum'),
        (LIVE_BUSY, '🔴 Gavjum / Joylar kam'),
    )

    business = models.ForeignKey(
        Business,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='locations',
        verbose_name='Biznes'
    )
    name = models.CharField(max_length=200, verbose_name='Joy nomi')
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default=CATEGORY_COWORKING, verbose_name='Kategoriya')
    district = models.CharField(max_length=40, choices=DISTRICT_CHOICES, default='chorsu', verbose_name='Tuman / Hudud')
    address = models.CharField(max_length=300, verbose_name='Aniq manzil')
    landmark = models.CharField(max_length=200, blank=True, verbose_name='Mo‘ljal')
    
    latitude = models.DecimalField(max_digits=9, decimal_places=6, default=41.311081, verbose_name='Kenglik (Latitude)')
    longitude = models.DecimalField(max_digits=9, decimal_places=6, default=69.240562, verbose_name='Uzunlik (Longitude)')

    phone = models.CharField(max_length=40, blank=True, verbose_name='Telefon')
    telegram = models.CharField(max_length=100, blank=True, verbose_name='Telegram')
    instagram = models.CharField(max_length=100, blank=True, verbose_name='Instagram')
    website = models.URLField(blank=True, verbose_name='Veb-sayt')

    description = models.TextField(verbose_name='Joy haqida batafsil')
    working_hours = models.CharField(max_length=100, default='08:00 - 23:00', verbose_name='Ish vaqti')
    is_24_7 = models.BooleanField(default=False, verbose_name='24/7 ochiq')

    hourly_price = models.DecimalField(max_digits=10, decimal_places=0, default=20000, verbose_name='1 soatlik narx (so‘m)')
    daily_price = models.DecimalField(max_digits=10, decimal_places=0, default=120000, verbose_name='Kunlik narx (so‘m)')
    currency = models.CharField(max_length=10, default='UZS', verbose_name='Valyuta')

    cover_image = models.ImageField(upload_to='locations/covers/', blank=True, null=True, verbose_name='Asosiy rasm')
    is_promoted = models.BooleanField(default=False, verbose_name='Promoted / Tavsiya etilgan')
    is_verified = models.BooleanField(default=True, verbose_name='Tasdiqlangan')
    is_active = models.BooleanField(default=True, verbose_name='Faol')

    # Live & Metrics
    live_status = models.CharField(max_length=20, choices=LIVE_STATUS_CHOICES, default=LIVE_QUIET, verbose_name='Hozirgi holat (Live)')
    live_status_updated_at = models.DateTimeField(auto_now=True, verbose_name='Live status yangilangan vaqt')
    
    current_db_level = models.FloatField(default=45.0, verbose_name='Hozirgi shovqin (dB)')
    avg_download_mbps = models.FloatField(default=120.0, verbose_name='Internet Download (Mbps)')
    avg_upload_mbps = models.FloatField(default=80.0, verbose_name='Internet Upload (Mbps)')
    avg_ping_ms = models.IntegerField(default=8, verbose_name='Ping (ms)')

    rating = models.FloatField(default=4.8, verbose_name='Reyting (1-5)')
    review_count = models.PositiveIntegerField(default=0, verbose_name='Sharhlar soni')
    total_visits = models.PositiveIntegerField(default=0, verbose_name='Jami tashriflar')

    amenities = models.ManyToManyField(Amenity, blank=True, related_name='locations', verbose_name='Qulayliklar')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Ishlash joyi (Location)'
        verbose_name_plural = 'Ishlash joylari'
        ordering = ['-is_promoted', '-rating', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name) or f"location-{self.id or 1}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.get_district_display()})"

    @property
    def live_badge_class(self):
        if self.live_status == self.LIVE_QUIET:
            return 'badge-quiet'
        elif self.live_status == self.LIVE_MODERATE:
            return 'badge-moderate'
        return 'badge-busy'

    @property
    def live_badge_text(self):
        if self.live_status == self.LIVE_QUIET:
            return 'Tinch & Bo‘sh joylar bor'
        elif self.live_status == self.LIVE_MODERATE:
            return 'O‘rtacha gavjum'
        return 'Gavjum'


class LocationImage(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='images', verbose_name='Joy')
    image = models.ImageField(upload_to='locations/gallery/', verbose_name='Rasm')
    caption = models.CharField(max_length=150, blank=True, verbose_name='Izoh')
    is_primary = models.BooleanField(default=False, verbose_name='Asosiy galereya rasmi')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Joy rasmi'
        verbose_name_plural = 'Joy rasmlari'


class Zone(models.Model):
    ZONE_QUIET = 'quiet_zone'
    ZONE_OPEN = 'open_space'
    ZONE_ZOOM = 'zoom_booth'
    ZONE_MEETING = 'meeting_room'
    ZONE_TERRACE = 'terrace'

    ZONE_TYPE_CHOICES = (
        (ZONE_QUIET, 'Tinch / Jimjit zona (Silent Zone)'),
        (ZONE_OPEN, 'Ochiq zal (Open Space)'),
        (ZONE_ZOOM, 'Zoom / Qo‘ng‘iroq kabinasi (Call Booth)'),
        (ZONE_MEETING, 'Uchrashuv xonasi (Meeting Room)'),
        (ZONE_TERRACE, 'Ochiq ayvon / Terassa'),
    )

    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='zones', verbose_name='Joy')
    name = models.CharField(max_length=100, verbose_name='Zona nomi')
    zone_type = models.CharField(max_length=30, choices=ZONE_TYPE_CHOICES, default=ZONE_QUIET, verbose_name='Zona turi')
    noise_level_expected = models.CharField(
        max_length=20,
        choices=(('silent', '< 40 dB (Mutlaq tinch)'), ('low', '40-50 dB (Qulay)'), ('normal', '50-65 dB (Faol)')),
        default='low',
        verbose_name='Kutiladigan shovqin'
    )
    capacity = models.PositiveIntegerField(default=10, verbose_name='Sig‘im (odam soni)')

    class Meta:
        verbose_name = 'Zona'
        verbose_name_plural = 'Zonalar'

    def __str__(self):
        return f"{self.location.name} — {self.name} ({self.get_zone_type_display()})"


class TableDesk(models.Model):
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='tables', verbose_name='Zona')
    table_number = models.CharField(max_length=50, verbose_name='Stol / Joy raqami')
    has_outlet = models.BooleanField(default=True, verbose_name='Rozetka mavjud')
    hourly_price = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True, verbose_name='Maxsus soatlik narx (so‘m)')
    is_active = models.BooleanField(default=True, verbose_name='Foydalanishga tayyor')

    class Meta:
        verbose_name = 'Stol / Ish o‘rni'
        verbose_name_plural = 'Stollar / Ish o‘rinlari'
        unique_together = ('zone', 'table_number')

    def __str__(self):
        return f"{self.zone.location.name} | {self.zone.name} | Stol {self.table_number}"

    @property
    def effective_hourly_price(self):
        if self.hourly_price:
            return self.hourly_price
        return self.zone.location.hourly_price
