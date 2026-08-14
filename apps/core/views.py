import json
from datetime import datetime, timedelta
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg, Count
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from apps.locations.models import Location, Zone, TableDesk, Amenity
from apps.bookings.models import Booking, CheckIn
from apps.payments.models import Payment, QuietPass, QuietPassPlan
from apps.reviews.models import Review
from apps.measurements.models import InternetTest, NoiseTest
from apps.ai_service.services import SmartMatchmaker, ReviewSummarizer, DemandNoisePredictor
from apps.core.models import Notification, AuditLog


def home_view(request):
    featured_locations = Location.objects.filter(is_active=True).prefetch_related('amenities').order_by('-is_promoted', '-rating')[:6]
    all_locations = Location.objects.filter(is_active=True).values('id', 'name', 'slug', 'category', 'district', 'latitude', 'longitude', 'live_status', 'hourly_price', 'rating', 'avg_download_mbps', 'current_db_level', 'address')
    amenities = Amenity.objects.all()[:8]
    quietpass_plans = QuietPassPlan.objects.filter(is_active=True)[:3]

    stats = {
        'total_spaces': Location.objects.filter(is_active=True).count(),
        'total_bookings': Booking.objects.count(),
        'total_tests': InternetTest.objects.count() + NoiseTest.objects.count(),
        'active_coworkings': Location.objects.filter(category='coworking', is_active=True).count(),
    }

    context = {
        'featured_locations': featured_locations,
        'locations_json': json.dumps(list(all_locations), default=str),
        'amenities': amenities,
        'quietpass_plans': quietpass_plans,
        'stats': stats,
    }
    return render(request, 'core/home.html', context)


def explore_map_view(request):
    locations = Location.objects.filter(is_active=True).prefetch_related('amenities', 'zones')

    # Filters
    district = request.GET.get('district')
    category = request.GET.get('category')
    live_status = request.GET.get('live_status')
    min_speed = request.GET.get('min_speed')
    max_noise = request.GET.get('max_noise')
    amenity_id = request.GET.get('amenity')
    search = request.GET.get('q')

    if district:
        locations = locations.filter(district=district)
    if category:
        locations = locations.filter(category=category)
    if live_status:
        locations = locations.filter(live_status=live_status)
    if min_speed:
        locations = locations.filter(avg_download_mbps__gte=float(min_speed))
    if max_noise:
        locations = locations.filter(current_db_level__lte=float(max_noise))
    if amenity_id:
        locations = locations.filter(amenities__id=amenity_id)
    if search:
        locations = locations.filter(
            Q(name__icontains=search) | Q(address__icontains=search) | Q(description__icontains=search)
        )

    all_amenities = Amenity.objects.all()
    districts = Location.DISTRICT_CHOICES
    categories = Location.CATEGORY_CHOICES

    # JSON for Leaflet Map
    map_data = []
    for loc in locations:
        map_data.append({
            'id': loc.id,
            'name': loc.name,
            'slug': loc.slug,
            'category': loc.get_category_display(),
            'district': loc.get_district_display(),
            'lat': float(loc.latitude),
            'lng': float(loc.longitude),
            'live_status': loc.live_status,
            'live_badge_text': loc.live_badge_text,
            'hourly_price': int(loc.hourly_price),
            'rating': loc.rating,
            'speed': loc.avg_download_mbps,
            'db': loc.current_db_level,
            'address': loc.address,
            'url': f"/locations/{loc.slug}/",
            'image': loc.cover_image.url if loc.cover_image else '',
        })

    context = {
        'locations': locations,
        'map_data_json': json.dumps(map_data),
        'all_amenities': all_amenities,
        'districts': districts,
        'categories': categories,
        'selected_district': district,
        'selected_category': category,
        'selected_live_status': live_status,
        'search_query': search,
    }
    return render(request, 'core/explore_map.html', context)


def location_detail_view(request, slug):
    location = get_object_or_404(
        Location.objects.prefetch_related('images', 'amenities', 'zones__tables', 'promotions'),
        slug=slug,
        is_active=True
    )
    
    # AI Modules
    ai_summary = ReviewSummarizer.summarize_location(location)
    ai_demand_forecast = DemandNoisePredictor.get_hourly_forecast(location)

    # Reviews
    reviews = Review.objects.filter(location=location, moderation_status='approved').select_related('user').order_by('-created_at')
    
    # Recent Measurements
    recent_speeds = InternetTest.objects.filter(location=location, is_verified=True).order_by('-created_at')[:5]
    recent_noise = NoiseTest.objects.filter(location=location, is_verified=True).order_by('-created_at')[:5]

    # Zones and tables for booking
    zones = location.zones.prefetch_related('tables').all()

    # User review submission check
    user_has_reviewed = False
    if request.user.is_authenticated:
        user_has_reviewed = Review.objects.filter(location=location, user=request.user).exists()

    context = {
        'location': location,
        'ai_summary': ai_summary,
        'ai_demand_forecast': ai_demand_forecast,
        'reviews': reviews,
        'recent_speeds': recent_speeds,
        'recent_noise': recent_noise,
        'zones': zones,
        'user_has_reviewed': user_has_reviewed,
    }
    return render(request, 'core/location_detail.html', context)


@login_required
def create_booking_view(request, location_id):
    location = get_object_or_404(Location, id=location_id, is_active=True)

    if request.method == 'POST':
        table_id = request.POST.get('table_id')
        zone_id = request.POST.get('zone_id')
        booking_date_str = request.POST.get('booking_date')
        start_time_str = request.POST.get('start_time')
        end_time_str = request.POST.get('end_time')

        if not (booking_date_str and start_time_str and end_time_str):
            messages.error(request, "Iltimos, sana va vaqt oraliqlarini to‘liq tanlang.")
            return redirect('core:location_detail', slug=location.slug)

        try:
            booking_date = datetime.strptime(booking_date_str, '%Y-%m-%d').date()
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.strptime(end_time_str, '%H:%M').time()
        except ValueError:
            messages.error(request, "Noto‘g‘ri sana yoki vaqt formati.")
            return redirect('core:location_detail', slug=location.slug)

        if start_time >= end_time:
            messages.error(request, "Tugash vaqti boshlanish vaqtidan keyin bo‘lishi shart.")
            return redirect('core:location_detail', slug=location.slug)

        # Calculate duration
        start_dt = datetime.combine(booking_date, start_time)
        end_dt = datetime.combine(booking_date, end_time)
        duration_hours = Decimal(str(round((end_dt - start_dt).total_seconds() / 3600, 1)))

        table = None
        zone = None
        if table_id:
            table = get_object_or_404(TableDesk, id=table_id)
            zone = table.zone
            # Check concurrency conflict!
            if Booking.check_conflict(table, booking_date, start_time, end_time):
                messages.error(request, f"Kechirasiz! Stol #{table.table_number} tanlangan vaqt oralig‘ida ({start_time_str} - {end_time_str}) allaqachon band qilingan. Iltimos, boshqa stol yoki vaqtni tanlang.")
                return redirect('core:location_detail', slug=location.slug)
        elif zone_id:
            zone = get_object_or_404(Zone, id=zone_id, location=location)

        # Price calculation
        hourly_rate = table.effective_hourly_price if table else location.hourly_price
        total_price = Decimal(hourly_rate) * duration_hours

        # QuietPass discount if user has active pass
        active_pass = QuietPass.objects.filter(user=request.user, status='active').first()
        if active_pass and active_pass.plan:
            discount_pct = active_pass.plan.discount_percent
            discount_amount = (total_price * Decimal(discount_pct)) / Decimal(100)
            total_price -= discount_amount

        booking = Booking.objects.create(
            user=request.user,
            location=location,
            zone=zone,
            table=table,
            booking_date=booking_date,
            start_time=start_time,
            end_time=end_time,
            total_hours=duration_hours,
            price_per_hour=hourly_rate,
            total_price=total_price,
            status='pending'
        )

        return redirect('core:checkout_booking', booking_id=booking.id)

    return redirect('core:location_detail', slug=location.slug)


@login_required
def checkout_booking_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if request.method == 'POST':
        provider = request.POST.get('provider', 'payme')
        receipt_file = request.FILES.get('receipt_image')

        payment = Payment.objects.create(
            user=request.user,
            booking=booking,
            payment_type='booking',
            provider=provider,
            amount=booking.total_price,
            status='pending',
            receipt_image=receipt_file
        )

        # If automated mockup provider (Click / Payme / Uzum test mode):
        if provider in ['click', 'payme', 'uzum']:
            # Auto-confirm pilot payment
            payment.accept_payment(
                admin_user=None,
                note=f"{provider.upper()} onlayn to‘lov tizimi orqali avtomatik tasdiqlandi."
            )
            messages.success(request, f"To‘lovingiz ({provider.upper()}) muvaffaqiyatli qabul qilindi! Joyingiz tasdiqlandi.")
            return redirect('core:my_bookings')
        else:
            # Manual transfer: pending admin review
            messages.info(request, "To‘lov cheki qabul qilindi. Administratorimiz tekshirgach, buyurtmangiz faollashtiriladi.")
            return redirect('core:my_bookings')

    context = {
        'booking': booking,
    }
    return render(request, 'core/checkout_booking.html', context)


@login_required
def my_bookings_view(request):
    bookings = Booking.objects.filter(user=request.user).select_related('location', 'table', 'zone').order_by('-booking_date', '-start_time')
    return render(request, 'core/my_bookings.html', {'bookings': bookings})


@login_required
def cancel_booking_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if request.method == 'POST':
        if booking.status in ['pending', 'confirmed']:
            booking.status = 'cancelled'
            booking.cancellation_reason = request.POST.get('reason', 'Foydalanuvchi tomonidan bekor qilindi')
            booking.save(update_fields=['status', 'cancellation_reason'])
            messages.success(request, f"Buyurtma #{booking.booking_code} bekor qilindi.")
    return redirect('core:my_bookings')


def quietpass_view(request):
    from apps.payments.models import SubscriptionRequest, ContactChannel

    plans = QuietPassPlan.objects.filter(is_active=True).order_by('order', 'price')
    contacts = ContactChannel.objects.filter(is_active=True).order_by('order')
    user_pass = None
    if request.user.is_authenticated:
        user_pass = QuietPass.objects.filter(user=request.user).order_by('-created_at').first()

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        telegram = request.POST.get('telegram', '').strip()
        plan_id = request.POST.get('plan_id')
        note = request.POST.get('note', '').strip()
        receipt_image = request.FILES.get('receipt_image')

        if not (full_name and phone and plan_id):
            messages.error(request, "Iltimos, ism, telefon raqami va tarifni to‘liq tanlang.")
            return redirect('core:quietpass')

        plan = get_object_or_404(QuietPassPlan, id=plan_id)
        user = request.user if request.user.is_authenticated else None

        # If user is not logged in, find by phone/username or create
        if not user:
            from apps.accounts.models import User
            clean_phone = phone.replace(' ', '').replace('+', '')
            user = User.objects.filter(phone_number=phone).first()
            if not user:
                user = User.objects.create(
                    username=f"user_{clean_phone[-6:]}" if len(clean_phone) >= 6 else f"user_{uuid.uuid4().hex[:6]}",
                    first_name=full_name,
                    phone_number=phone,
                    telegram_username=telegram.lstrip('@'),
                    role=User.ROLE_USER
                )
                user.set_unusable_password()
                user.save()

        # Create Subscription Request
        sub_req = SubscriptionRequest.objects.create(
            user=user,
            full_name=full_name,
            phone=phone,
            telegram=telegram,
            plan=plan,
            plan_days=plan.duration_days,
            amount=plan.price,
            receipt_image=receipt_image,
            note=note,
            status=SubscriptionRequest.Status.NEW
        )

        # Create QuietPass in pending state
        qp = QuietPass.objects.create(
            user=user,
            plan=plan,
            plan_name=plan.name,
            price=plan.price,
            status='pending'
        )

        # Create Payment in pending state for admin review
        Payment.objects.create(
            user=user,
            quietpass=qp,
            subscription_request=sub_req,
            payment_type='quietpass',
            provider='manual_transfer',
            amount=plan.price,
            status='pending',
            receipt_image=receipt_image,
            admin_note=f"So‘rov: {full_name} (Tel: {phone}, TG: {telegram}). Izoh: {note}"
        )

        # Notify admins
        from apps.accounts.models import User
        admin_users = User.objects.filter(role__in=[User.ROLE_SUPERADMIN, User.ROLE_PAYMENT_ADMIN])
        for adm in admin_users:
            Notification.objects.create(
                user=adm,
                title='Yangi QuietPass so‘rovi!',
                message=f"{full_name} ({phone}) {plan.name} uchun so‘rov yubordi. Summa: {plan.price:,.0f} so‘m.",
                notification_type='quietpass_status'
            )

        messages.success(
            request,
            f"Rahmat, {full_name}! {plan.name} bo‘yicha so‘rovingiz administratorga yuborildi. Tez orada tekshirilib, obunangiz faollashtiriladi."
        )
        return redirect('core:quietpass')

    context = {
        'plans': plans,
        'contacts': contacts,
        'user_pass': user_pass,
    }
    return render(request, 'core/quietpass.html', context)


@login_required
def buy_quietpass_view(request, plan_id):
    plan = get_object_or_404(QuietPassPlan, id=plan_id, is_active=True)

    if request.method == 'POST':
        provider = request.POST.get('provider', 'payme')
        receipt_file = request.FILES.get('receipt_image')

        quietpass = QuietPass.objects.create(
            user=request.user,
            plan=plan,
            plan_name=plan.name,
            price=plan.price,
            status='pending'
        )

        payment = Payment.objects.create(
            user=request.user,
            quietpass=quietpass,
            payment_type='quietpass',
            provider=provider,
            amount=plan.price,
            status='pending',
            receipt_image=receipt_file
        )

        if provider in ['click', 'payme', 'uzum']:
            payment.accept_payment(admin_user=None, note=f"{provider.upper()} orqali to‘landi.")
            messages.success(request, f"Tabriklaymiz! {plan.name} obunangiz faollashtirildi.")
            return redirect('core:quietpass')
        else:
            messages.info(request, "Obuna so‘rovi va to‘lov cheki qabul qilindi. Admin tasdiqlashini kuting.")
            return redirect('core:quietpass')

    return render(request, 'core/checkout_quietpass.html', {'plan': plan})


@login_required
def submit_review_view(request, location_id):
    location = get_object_or_404(Location, id=location_id)

    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        title = request.POST.get('title', '')
        text = request.POST.get('text', '')
        image = request.FILES.get('image')
        noise_rating = int(request.POST.get('noise_rating', 5))
        wifi_rating = int(request.POST.get('wifi_rating', 5))
        comfort_rating = int(request.POST.get('comfort_rating', 5))

        if not text:
            messages.error(request, "Sharh matnini yozishingiz kerak.")
            return redirect('core:location_detail', slug=location.slug)

        # Check if verified visitor
        has_visited = CheckIn.objects.filter(user=request.user, location=location).exists()

        Review.objects.create(
            location=location,
            user=request.user,
            rating=rating,
            title=title,
            text=text,
            image=image,
            noise_rating=noise_rating,
            wifi_rating=wifi_rating,
            comfort_rating=comfort_rating,
            is_verified_visitor=has_visited,
            moderation_status='approved'
        )
        pts = 20 if image else 10
        messages.success(request, f"Sharhingiz qabul qilindi! Sizga +{pts} ball berildi.")
        return redirect('core:location_detail', slug=location.slug)

    return redirect('core:location_detail', slug=location.slug)


@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    # Mark all read
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return render(request, 'core/notifications.html', {'notifications': notifications})


# =========================================================
# PAYMENT ADMIN & SUPER ADMIN MANAGEMENT
# =========================================================

def payment_admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not (request.user.is_payment_admin_user or request.user.is_superuser):
            messages.error(request, "Ushbu bo‘lim faqat To‘lov Administratorlari uchun.")
            return redirect('core:home')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@payment_admin_required
def admin_payment_management_view(request):
    status_filter = request.GET.get('status', 'pending')
    payments = Payment.objects.all().select_related('user', 'booking', 'quietpass', 'processed_by', 'subscription_request')
    
    if status_filter != 'all':
        payments = payments.filter(status=status_filter)

    payments = payments.order_by('-created_at')

    stats = {
        'pending': Payment.objects.filter(status='pending').count(),
        'paid': Payment.objects.filter(status='paid').count(),
        'rejected': Payment.objects.filter(status='rejected').count(),
        'total_volume': Payment.objects.filter(status='paid').aggregate(total=Avg('amount'))['total'] or 0,
    }

    recent_audits = AuditLog.objects.filter(action__in=['payment_accept', 'payment_reject', 'manual_subscription_activate']).order_by('-created_at')[:10]

    context = {
        'payments': payments,
        'status_filter': status_filter,
        'stats': stats,
        'recent_audits': recent_audits,
    }
    return render(request, 'admin_panel/payment_management.html', context)


@login_required
@payment_admin_required
def admin_payment_action_view(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        note = request.POST.get('note', '')

        if action == 'accept':
            payment.accept_payment(admin_user=request.user, note=note or "Admin tomonidan tasdiqlandi")
            messages.success(request, f"To‘lov #{payment.transaction_id} TASDIQLANDI va xizmat faollashtirildi.")
        elif action == 'reject':
            payment.reject_payment(admin_user=request.user, reason=note or "To‘lov rad etildi")
            messages.warning(request, f"To‘lov #{payment.transaction_id} RAD ETILDI.")
        elif action == 'manual_activate':
            if payment.quietpass:
                payment.quietpass.status = 'active'
                payment.quietpass.start_date = timezone.now().date()
                payment.quietpass.end_date = timezone.now().date() + timedelta(days=30)
                payment.quietpass.save()
            payment.status = 'paid'
            payment.save()
            AuditLog.objects.create(
                admin_user=request.user,
                action='manual_subscription_activate',
                target_model='QuietPass',
                target_id=str(payment.id),
                details=f"Admin tomonidan qo‘lda ACTIVE qilindi. Sabab: {note}"
            )
            messages.success(request, "Qo‘lda faollashtirildi va AuditLogga yozildi.")

    return redirect('core:admin_payments')


@login_required
def admin_audit_log_view(request):
    if not request.user.is_superuser:
        messages.error(request, "Ruxsat etilmagan.")
        return redirect('core:home')

    logs = AuditLog.objects.all().select_related('admin_user').order_by('-created_at')
    return render(request, 'admin_panel/audit_logs.html', {'logs': logs})
