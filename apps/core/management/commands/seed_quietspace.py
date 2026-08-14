import random
from datetime import date, time, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.accounts.models import User
from apps.locations.models import Business, Amenity, Location, Zone, TableDesk
from apps.measurements.models import InternetTest, NoiseTest
from apps.bookings.models import Booking, CheckIn
from apps.payments.models import QuietPassPlan, QuietPass, Payment
from apps.reviews.models import Review
from apps.gamification.models import Promotion, RewardTransaction
from apps.core.models import Notification, AuditLog


class Command(BaseCommand):
    help = 'QuietSpace Tashkent uchun demo ma’lumotlarni yuklash'

    def handle(self, *args, **options):
        self.stdout.write("QuietSpace ma’lumotlari yuklanmoqda...")

        # 1. Super Admin
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@quietspace.uz',
                'first_name': 'Super',
                'last_name': 'Admin',
                'role': User.ROLE_SUPERADMIN,
                'is_staff': True,
                'is_superuser': True,
                'points': 1000,
                'status_tier': User.TIER_SPACE_GURU,
            }
        )
        admin_user.set_password('admin12345')
        admin_user.save()

        # Payment Admin
        pay_admin, _ = User.objects.get_or_create(
            username='payadmin',
            defaults={
                'email': 'pay@quietspace.uz',
                'first_name': 'To‘lov',
                'last_name': 'Nazoratchisi',
                'role': User.ROLE_PAYMENT_ADMIN,
                'is_staff': True,
            }
        )
        pay_admin.set_password('payadmin123')
        pay_admin.save()

        # Business Owners
        owner_cspace, _ = User.objects.get_or_create(
            username='cspace_owner',
            defaults={
                'email': 'cspace@quietspace.uz',
                'first_name': 'Alisher',
                'last_name': 'Raximov',
                'role': User.ROLE_BUSINESS_OWNER,
            }
        )
        owner_cspace.set_password('owner12345')
        owner_cspace.save()

        owner_gz, _ = User.objects.get_or_create(
            username='gz_owner',
            defaults={
                'email': 'groundzero@quietspace.uz',
                'first_name': 'Temur',
                'last_name': 'Saidov',
                'role': User.ROLE_BUSINESS_OWNER,
            }
        )
        owner_gz.set_password('owner12345')
        owner_gz.save()

        # Demo regular users
        student, _ = User.objects.get_or_create(
            username='student',
            defaults={
                'email': 'student@edu.uz',
                'first_name': 'Azizbek',
                'last_name': 'Toshmatov',
                'role': User.ROLE_USER,
                'points': 40,
                'status_tier': User.TIER_EXPLORER,
            }
        )
        student.set_password('student123')
        student.save()

        freelancer, _ = User.objects.get_or_create(
            username='freelancer',
            defaults={
                'email': 'freelance@gmail.com',
                'first_name': 'Jasur',
                'last_name': 'Kamilov',
                'role': User.ROLE_USER,
                'points': 280,
                'status_tier': User.TIER_QUIET_MASTER,
                'telegram_username': 'jasur_dev',
            }
        )
        freelancer.set_password('freelancer123')
        freelancer.save()

        guru_user, _ = User.objects.get_or_create(
            username='guru_user',
            defaults={
                'email': 'guru@quietspace.uz',
                'first_name': 'Nodir',
                'last_name': 'Zokirov',
                'role': User.ROLE_USER,
                'points': 620,
                'status_tier': User.TIER_SPACE_GURU,
                'telegram_username': 'nodir_guru',
            }
        )
        guru_user.set_password('guru12345')
        guru_user.save()

        # 2. Businesses
        biz_cspace, _ = Business.objects.get_or_create(
            owner=owner_cspace,
            name='C-Space LLC',
            defaults={
                'brand_name': 'C-Space Tashkent',
                'phone': '+998 71 200 00 11',
                'is_verified': True,
                'description': 'Toshkentdagi yetakchi kovorking tarmoqlari.'
            }
        )

        biz_gz, _ = Business.objects.get_or_create(
            owner=owner_gz,
            name='Ground Zero Co-working',
            defaults={
                'brand_name': 'GroundZero Hub',
                'phone': '+998 90 999 88 77',
                'is_verified': True,
                'description': 'Innovatsion frilanserlar va startaplar markazi.'
            }
        )

        # 3. Amenities
        amenity_data = [
            ('Har bir stolda rozetka', 'outlet', 'bi-plug-fill', 'connectivity'),
            ('Optik tola Wi-Fi (100+ Mbps)', 'high-speed-wifi', 'bi-wifi', 'connectivity'),
            ('Zoom / Ovoz o‘tkazmaydigan kabina', 'zoom-booth', 'bi-mic-fill', 'connectivity'),
            ('Ergonomik stullar va keng stollar', 'ergonomic-furniture', 'bi-briefcase-fill', 'comfort'),
            ('Konditsioner & Havo tozalagich', 'air-conditioning', 'bi-snow', 'comfort'),
            ('Bepul Qahva va Choy burchagi', 'free-coffee', 'bi-cup-hot-fill', 'facility'),
            ('24/7 Tunu-kun ochiq', 'open-24-7', 'bi-clock-history', 'facility'),
            ('Avtoturargoh (Parking)', 'parking', 'bi-p-circle-fill', 'facility'),
            ('Printer va Skanner xizmati', 'printer', 'bi-printer-fill', 'facility'),
            ('Yashil hovli / Terassa', 'terrace', 'bi-tree-fill', 'comfort'),
        ]

        amenities_objs = {}
        for name, slug, icon, cat in amenity_data:
            am, _ = Amenity.objects.get_or_create(slug=slug, defaults={'name': name, 'icon': icon, 'category': cat})
            amenities_objs[slug] = am

        # 4. QuietPass Plans
        qp_weekly, _ = QuietPassPlan.objects.get_or_create(
            plan_code='weekly',
            defaults={
                'name': 'Haftalik QuietPass',
                'price': 89000,
                'duration_days': 7,
                'discount_percent': 10,
                'free_beverage_daily': True,
                'description': '7 kun davomida istalgan hamkor joyda 10% chegirma va kuniga 1 ta bepul kofe.'
            }
        )

        qp_monthly, _ = QuietPassPlan.objects.get_or_create(
            plan_code='monthly',
            defaults={
                'name': 'Oylik QuietPass Pro',
                'price': 290000,
                'duration_days': 30,
                'discount_percent': 20,
                'free_beverage_daily': True,
                'description': '30 kun davomida 20% chegirma, Zoom kabinasidan 5 soat bepul foydalanish va kunlik qahva.'
            }
        )

        qp_quarterly, _ = QuietPassPlan.objects.get_or_create(
            plan_code='quarterly',
            defaults={
                'name': 'Kvartallik VIP Pass',
                'price': 750000,
                'duration_days': 90,
                'discount_percent': 30,
                'free_beverage_daily': True,
                'description': '90 kunlik cheksiz imtiyozlar: 30% chegirma, ustuvor bron qilish va doimiy bepul ichimliklar.'
            }
        )

        # 5. Locations in Tashkent
        locations_data = [
            {
                'name': 'C-Space Chorsu',
                'slug': 'c-space-chorsu',
                'business': biz_cspace,
                'category': 'coworking',
                'district': 'chorsu',
                'address': 'Toshkent sh., Shayxontohur tumani, Zarqaynar ko‘chasi, 14-uy',
                'landmark': 'Chorsu bozori va Xadra yonida',
                'lat': 41.326840,
                'lng': 69.239410,
                'phone': '+998 71 200 11 22',
                'description': 'Chorsu markazida joylashgan zamonaviy va juda tinch kovorking. Tezkor 150 Mbps internet, shovqinsiz jimjit zona va alohida Zoom kabinalari mavjud.',
                'working_hours': '08:00 - 23:00',
                'is_24_7': False,
                'hourly_price': 25000,
                'daily_price': 140000,
                'live_status': 'quiet',
                'current_db_level': 41.5,
                'avg_download_mbps': 165.0,
                'avg_upload_mbps': 110.0,
                'avg_ping_ms': 6,
                'rating': 4.9,
                'review_count': 38,
                'is_promoted': True,
                'amenities': ['outlet', 'high-speed-wifi', 'zoom-booth', 'ergonomic-furniture', 'air-conditioning', 'free-coffee', 'parking'],
            },
            {
                'name': 'GroundZero Minor Hub',
                'slug': 'groundzero-minor',
                'business': biz_gz,
                'category': 'coworking',
                'district': 'yunusobod',
                'address': 'Toshkent sh., Yunusobod tumani, Minor metro yaqinida, Amir Temur shox ko‘chasi, 107B',
                'landmark': 'Minor masjidi ro‘parasida',
                'lat': 41.332500,
                'lng': 69.281200,
                'phone': '+998 90 999 88 77',
                'description': '24/7 ishlaydigan noutbuk bilan qulay ishlash maydoni. Yuqori tezlikdagi optik tola internet, audio yozuv va podkast xonasi, qulay kofe burchagi.',
                'working_hours': '24/7 Ochiq',
                'is_24_7': True,
                'hourly_price': 28000,
                'daily_price': 160000,
                'live_status': 'moderate',
                'current_db_level': 44.0,
                'avg_download_mbps': 210.0,
                'avg_upload_mbps': 180.0,
                'avg_ping_ms': 5,
                'rating': 4.8,
                'review_count': 52,
                'is_promoted': True,
                'amenities': ['outlet', 'high-speed-wifi', 'zoom-booth', 'ergonomic-furniture', 'air-conditioning', 'free-coffee', 'open-24-7', 'parking'],
            },
            {
                'name': 'Impact Hub Tashkent',
                'slug': 'impact-hub-tashkent',
                'business': biz_cspace,
                'category': 'coworking',
                'district': 'mirzo_ulugbek',
                'address': 'Toshkent sh., Mirzo Ulug‘bek tumani, Buyuk Ipak Yo‘li ko‘chasi, 45',
                'landmark': 'Sayohat mehmonxonasi yonida',
                'lat': 41.328900,
                'lng': 69.335400,
                'phone': '+998 71 207 70 00',
                'description': 'Frilanserlar va xalqaro jamoalar uchun sokin ish makoni. Yashil terassa, keng stol va rozetkalar, barqaror Wi-Fi va muzokaralar zali.',
                'working_hours': '08:30 - 22:30',
                'is_24_7': False,
                'hourly_price': 22000,
                'daily_price': 130000,
                'live_status': 'quiet',
                'current_db_level': 39.8,
                'avg_download_mbps': 135.0,
                'avg_upload_mbps': 90.0,
                'avg_ping_ms': 7,
                'rating': 4.9,
                'review_count': 29,
                'is_promoted': False,
                'amenities': ['outlet', 'high-speed-wifi', 'ergonomic-furniture', 'air-conditioning', 'free-coffee', 'terrace', 'parking'],
            },
            {
                'name': 'Ecorn Quiet Work Lounge',
                'slug': 'ecorn-work-lounge',
                'business': None,
                'category': 'cafe',
                'district': 'mirobod',
                'address': 'Toshkent sh., Mirobod tumani, Oybek ko‘chasi, 24/1',
                'landmark': 'Oybek metrosi yaqinida',
                'lat': 41.298500,
                'lng': 69.278900,
                'phone': '+998 97 700 33 44',
                'description': 'Frilanserlar uchun maxsus jimjit burchakka ega artisan qahvaxona. Tezkor Wi-Fi, har bir burchakda tok manbasi va yangi qovurilgan sara kofe.',
                'working_hours': '08:00 - 23:00',
                'is_24_7': False,
                'hourly_price': 18000,
                'daily_price': 95000,
                'live_status': 'moderate',
                'current_db_level': 47.5,
                'avg_download_mbps': 95.0,
                'avg_upload_mbps': 65.0,
                'avg_ping_ms': 11,
                'rating': 4.7,
                'review_count': 44,
                'is_promoted': False,
                'amenities': ['outlet', 'high-speed-wifi', 'air-conditioning', 'free-coffee'],
            },
            {
                'name': 'Alisher Navoiy Milliy Kutubxonasi Study Zone',
                'slug': 'navoiy-study-zone',
                'business': None,
                'category': 'library',
                'district': 'yakkasaroy',
                'address': 'Toshkent sh., Navoiy ko‘chasi, 1-uy',
                'landmark': 'Mustaqillik maydoni yaqinida',
                'lat': 41.316700,
                'lng': 69.266700,
                'phone': '+998 71 232 83 94',
                'description': 'Mutlaq sukunat va diqqatni jamlash uchun shahar markazidagi eng yirik kutubxona o‘quv zali. Shovqin darajasi 36 dB dan oshmaydi.',
                'working_hours': '09:00 - 21:00',
                'is_24_7': False,
                'hourly_price': 10000,
                'daily_price': 40000,
                'live_status': 'quiet',
                'current_db_level': 35.5,
                'avg_download_mbps': 90.0,
                'avg_upload_mbps': 55.0,
                'avg_ping_ms': 9,
                'rating': 4.9,
                'review_count': 67,
                'is_promoted': False,
                'amenities': ['outlet', 'high-speed-wifi', 'ergonomic-furniture', 'air-conditioning'],
            },
            {
                'name': 'Book Cafe Chilonzor',
                'slug': 'book-cafe-chilonzor',
                'business': None,
                'category': 'study_zone',
                'district': 'chilonzor',
                'address': 'Toshkent sh., Chilonzor tumani, Muqimiy ko‘chasi, 15',
                'landmark': 'Novza metrosi orqasida',
                'lat': 41.285400,
                'lng': 69.214500,
                'phone': '+998 90 123 45 67',
                'description': 'Talabalar va dasturchilar uchun qulay study space. Dars qilish, kod yozish va sokin muhitda fikr jamlash uchun moslashtirilgan.',
                'working_hours': '09:00 - 23:00',
                'is_24_7': False,
                'hourly_price': 15000,
                'daily_price': 80000,
                'live_status': 'quiet',
                'current_db_level': 43.0,
                'avg_download_mbps': 110.0,
                'avg_upload_mbps': 75.0,
                'avg_ping_ms': 8,
                'rating': 4.7,
                'review_count': 23,
                'is_promoted': False,
                'amenities': ['outlet', 'high-speed-wifi', 'ergonomic-furniture', 'air-conditioning', 'free-coffee'],
            }
        ]

        created_locations = []
        for l_data in locations_data:
            loc, created = Location.objects.get_or_create(
                slug=l_data['slug'],
                defaults={
                    'name': l_data['name'],
                    'business': l_data['business'],
                    'category': l_data['category'],
                    'district': l_data['district'],
                    'address': l_data['address'],
                    'landmark': l_data['landmark'],
                    'latitude': l_data['lat'],
                    'longitude': l_data['lng'],
                    'phone': l_data['phone'],
                    'description': l_data['description'],
                    'working_hours': l_data['working_hours'],
                    'is_24_7': l_data['is_24_7'],
                    'hourly_price': l_data['hourly_price'],
                    'daily_price': l_data['daily_price'],
                    'live_status': l_data['live_status'],
                    'current_db_level': l_data['current_db_level'],
                    'avg_download_mbps': l_data['avg_download_mbps'],
                    'avg_upload_mbps': l_data['avg_upload_mbps'],
                    'avg_ping_ms': l_data['avg_ping_ms'],
                    'rating': l_data['rating'],
                    'review_count': l_data['review_count'],
                    'is_promoted': l_data['is_promoted'],
                    'is_verified': True,
                    'is_active': True,
                }
            )
            # Set amenities
            for am_slug in l_data['amenities']:
                if am_slug in amenities_objs:
                    loc.amenities.add(amenities_objs[am_slug])

            created_locations.append(loc)

            # Create Zones and Tables
            z1, _ = Zone.objects.get_or_create(
                location=loc,
                name='Jimjit Zona (Silent Focus)',
                defaults={'zone_type': 'quiet_zone', 'noise_level_expected': 'silent', 'capacity': 12}
            )
            for i in range(1, 6):
                TableDesk.objects.get_or_create(zone=z1, table_number=f"S-{i}", defaults={'has_outlet': True})

            z2, _ = Zone.objects.get_or_create(
                location=loc,
                name='Ochiq Zal (Open Work)',
                defaults={'zone_type': 'open_space', 'noise_level_expected': 'low', 'capacity': 20}
            )
            for i in range(1, 8):
                TableDesk.objects.get_or_create(zone=z2, table_number=f"O-{i}", defaults={'has_outlet': True})

            z3, _ = Zone.objects.get_or_create(
                location=loc,
                name='Zoom & Call Kabinasi',
                defaults={'zone_type': 'zoom_booth', 'noise_level_expected': 'silent', 'capacity': 1}
            )
            TableDesk.objects.get_or_create(zone=z3, table_number="Zoom-1", defaults={'has_outlet': True, 'hourly_price': loc.hourly_price + 10000})

            # Create sample tests
            InternetTest.objects.create(
                location=loc,
                user=freelancer,
                download_mbps=loc.avg_download_mbps,
                upload_mbps=loc.avg_upload_mbps,
                ping_ms=loc.avg_ping_ms,
                source='platform_speedtest',
                freshness_status='fresh'
            )

            NoiseTest.objects.create(
                location=loc,
                user=freelancer,
                db_level=loc.current_db_level,
                duration_seconds=15,
                source='decibel_meter',
                freshness_status='fresh'
            )

            # Create sample reviews
            Review.objects.get_or_create(
                location=loc,
                user=freelancer,
                defaults={
                    'rating': 5,
                    'title': 'Juda sokin va qulay joy!',
                    'text': f"{loc.name} da kun bo‘yi ishladim. Internet tezligi juda barqaror, 150+ Mbps bemalol chiqdi. Rozetkalar har bir stolda bor. Kofe ham ajoyib.",
                    'noise_rating': 5,
                    'wifi_rating': 5,
                    'comfort_rating': 5,
                    'is_verified_visitor': True,
                    'moderation_status': 'approved'
                }
            )

            Review.objects.get_or_create(
                location=loc,
                user=guru_user,
                defaults={
                    'rating': 5,
                    'title': 'Masofaviy dasturchilar uchun ideal',
                    'text': 'Zoom kabinasidan onlayn uchrashuv o‘tkazdim, tashqi tovushlar umuman eshitilmadi. Kreslolari juda qulay, bel og‘rimaydi.',
                    'noise_rating': 5,
                    'wifi_rating': 5,
                    'comfort_rating': 5,
                    'is_verified_visitor': True,
                    'moderation_status': 'approved'
                }
            )

        # 6. Sample Active QuietPass for freelancer
        user_qp, _ = QuietPass.objects.get_or_create(
            user=freelancer,
            defaults={
                'plan': qp_monthly,
                'plan_name': qp_monthly.name,
                'price': qp_monthly.price,
                'status': 'active',
                'start_date': date.today() - timedelta(days=5),
                'end_date': date.today() + timedelta(days=25),
            }
        )

        # 7. Sample Bookings & Payments
        first_loc = created_locations[0]
        sample_table = TableDesk.objects.filter(zone__location=first_loc).first()

        sample_booking, _ = Booking.objects.get_or_create(
            booking_code='QS-998877',
            defaults={
                'user': freelancer,
                'location': first_loc,
                'zone': sample_table.zone if sample_table else None,
                'table': sample_table,
                'booking_date': date.today(),
                'start_time': time(14, 0),
                'end_time': time(18, 0),
                'total_hours': 4.0,
                'price_per_hour': first_loc.hourly_price,
                'total_price': first_loc.hourly_price * 4,
                'status': 'confirmed',
            }
        )

        sample_payment, _ = Payment.objects.get_or_create(
            transaction_id='TX-DEMO-PAYME-1',
            defaults={
                'user': freelancer,
                'booking': sample_booking,
                'payment_type': 'booking',
                'provider': 'payme',
                'amount': sample_booking.total_price,
                'status': 'paid',
                'processed_by': admin_user,
                'processed_at': timezone.now(),
                'admin_note': 'Avtomatik Payme orqali tasdiqlangan.'
            }
        )

        # Pending Payment example for Admin Management testing
        pending_booking, _ = Booking.objects.get_or_create(
            booking_code='QS-112233',
            defaults={
                'user': student,
                'location': created_locations[1],
                'booking_date': date.today() + timedelta(days=1),
                'start_time': time(10, 0),
                'end_time': time(13, 0),
                'total_hours': 3.0,
                'price_per_hour': created_locations[1].hourly_price,
                'total_price': created_locations[1].hourly_price * 3,
                'status': 'pending',
            }
        )

        Payment.objects.get_or_create(
            transaction_id='TX-MANUAL-CHECK-1',
            defaults={
                'user': student,
                'booking': pending_booking,
                'payment_type': 'booking',
                'provider': 'manual_transfer',
                'amount': pending_booking.total_price,
                'status': 'pending',
                'admin_note': 'Foydalanuvchi karta orqali to‘lov chekini yuklagan. Tekshiruv kutilmoqda.'
            }
        )

        # Promotions
        Promotion.objects.get_or_create(
            location=first_loc,
            title='Ertalabki 20% chegirma',
            defaults={
                'description': 'Soat 08:00 dan 12:00 gacha barcha ish stollariga 20% maxsus chegirma!',
                'discount_percent': 20,
                'start_date': date.today(),
                'end_date': date.today() + timedelta(days=30),
                'is_active': True
            }
        )

        self.stdout.write(self.style.SUCCESS("QuietSpace Tashkent demo ma’lumotlari muvaffaqiyatli yuklandi!"))
        self.stdout.write("Admin login: admin / admin12345")
        self.stdout.write("To‘lov admini: payadmin / payadmin123")
        self.stdout.write("Biznes egasi: cspace_owner / owner12345")
        self.stdout.write("Foydalanuvchilar: freelancer / freelancer123, student / student123")
