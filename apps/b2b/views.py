from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from apps.locations.models import Business, Location, Zone, TableDesk
from apps.bookings.models import Booking, CheckIn
from apps.gamification.models import Promotion
from apps.reviews.models import Review


def b2b_owner_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not (request.user.is_business or request.user.is_superuser):
            messages.warning(request, "Bu bo‘lim faqat B2B hamkorlar va Biznes egalari uchun.")
            return redirect('core:home')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@b2b_owner_required
def b2b_dashboard(request):
    user = request.user
    if user.is_superuser:
        locations = Location.objects.all()
    else:
        business = Business.objects.filter(owner=user).first()
        locations = Location.objects.filter(business=business) if business else Location.objects.filter(business__owner=user)

    total_locations = locations.count()
    active_bookings = Booking.objects.filter(location__in=locations, status__in=['pending', 'confirmed']).count()
    today_checkins = CheckIn.objects.filter(location__in=locations, created_at__date=timezone.now().date()).count()
    total_revenue = Booking.objects.filter(location__in=locations, status__in=['confirmed', 'checked_in', 'completed']).aggregate(Sum('total_price'))['total_price__sum'] or 0

    recent_bookings = Booking.objects.filter(location__in=locations).select_related('user', 'table', 'location').order_by('-created_at')[:8]
    recent_reviews = Review.objects.filter(location__in=locations).select_related('user', 'location').order_by('-created_at')[:5]

    context = {
        'locations': locations,
        'total_locations': total_locations,
        'active_bookings': active_bookings,
        'today_checkins': today_checkins,
        'total_revenue': total_revenue,
        'recent_bookings': recent_bookings,
        'recent_reviews': recent_reviews,
    }
    return render(request, 'b2b/dashboard.html', context)


@login_required
@b2b_owner_required
def b2b_set_live_status(request, location_id):
    if request.method == 'POST':
        location = get_object_or_404(Location, id=location_id)
        # Check permissions
        if not (request.user.is_superuser or (location.business and location.business.owner == request.user)):
            return JsonResponse({'status': 'error', 'message': 'Ruxsat berilmagan'}, status=403)
        
        status = request.POST.get('live_status')
        if status in ['quiet', 'moderate', 'busy']:
            location.live_status = status
            location.save(update_fields=['live_status', 'live_status_updated_at'])
            messages.success(request, f"{location.name} holati o‘zgartirildi: {location.get_live_status_display()}")
        return redirect('b2b:dashboard')
    return redirect('b2b:dashboard')


@login_required
@b2b_owner_required
def b2b_verify_checkin(request):
    search_query = request.GET.get('code', '').strip()
    booking = None
    if search_query:
        booking = Booking.objects.filter(booking_code__iexact=search_query).select_related('user', 'location', 'table').first()

    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        booking = get_object_or_404(Booking, id=booking_id)
        booking.status = 'checked_in'
        booking.save(update_fields=['status'])

        CheckIn.objects.create(
            booking=booking,
            location=booking.location,
            user=booking.user,
            check_in_code=booking.booking_code,
            method='code_manual',
            is_verified=True
        )
        messages.success(request, f"Mijoz {booking.user.username} ({booking.booking_code}) muvaffaqiyatli qabul qilindi!")
        return redirect('b2b:checkin')

    return render(request, 'b2b/checkin.html', {'booking': booking, 'code': search_query})


@login_required
@b2b_owner_required
def b2b_bookings_list(request):
    user = request.user
    if user.is_superuser:
        bookings = Booking.objects.all()
    else:
        bookings = Booking.objects.filter(location__business__owner=user)
    
    status_filter = request.GET.get('status')
    if status_filter:
        bookings = bookings.filter(status=status_filter)

    bookings = bookings.select_related('user', 'location', 'table', 'zone').order_by('-booking_date', '-start_time')
    return render(request, 'b2b/bookings_list.html', {'bookings': bookings, 'status_filter': status_filter})


@login_required
@b2b_owner_required
def b2b_inventory(request, location_id):
    location = get_object_or_404(Location, id=location_id)
    zones = location.zones.prefetch_related('tables').all()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_zone':
            name = request.POST.get('name')
            zone_type = request.POST.get('zone_type', 'quiet_zone')
            capacity = int(request.POST.get('capacity', 10))
            Zone.objects.create(location=location, name=name, zone_type=zone_type, capacity=capacity)
            messages.success(request, f"Yangi zona '{name}' qo‘shildi.")
        elif action == 'add_table':
            zone_id = request.POST.get('zone_id')
            zone = get_object_or_404(Zone, id=zone_id, location=location)
            table_number = request.POST.get('table_number')
            has_outlet = bool(request.POST.get('has_outlet'))
            TableDesk.objects.create(zone=zone, table_number=table_number, has_outlet=has_outlet)
            messages.success(request, f"Stol #{table_number} qo‘shildi.")
        return redirect('b2b:inventory', location_id=location.id)

    return render(request, 'b2b/inventory.html', {'location': location, 'zones': zones})


@login_required
@b2b_owner_required
def b2b_promotions(request):
    user = request.user
    if user.is_superuser:
        locations = Location.objects.all()
        promotions = Promotion.objects.all()
    else:
        locations = Location.objects.filter(business__owner=user)
        promotions = Promotion.objects.filter(location__in=locations)

    if request.method == 'POST':
        loc_id = request.POST.get('location_id')
        title = request.POST.get('title')
        description = request.POST.get('description')
        discount = int(request.POST.get('discount_percent', 10))
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        loc = get_object_or_404(Location, id=loc_id)
        Promotion.objects.create(
            location=loc,
            title=title,
            description=description,
            discount_percent=discount,
            start_date=start_date,
            end_date=end_date
        )
        messages.success(request, f"Yangi aksiya '{title}' muvaffaqiyatli yaratildi.")
        return redirect('b2b:promotions')

    return render(request, 'b2b/promotions.html', {'promotions': promotions, 'locations': locations})
