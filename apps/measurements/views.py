import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from apps.locations.models import Location
from .models import InternetTest, NoiseTest


@login_required
@csrf_exempt
def submit_speedtest_api(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST metodi talab qilinadi'}, status=405)
    
    try:
        data = json.loads(request.body)
        location_id = data.get('location_id')
        download_mbps = float(data.get('download_mbps', 0))
        upload_mbps = float(data.get('upload_mbps', 0))
        ping_ms = int(data.get('ping_ms', 10))

        if not location_id or download_mbps <= 0:
            return JsonResponse({'status': 'error', 'message': 'Noto‘g‘ri ma’lumotlar kiritildi'}, status=400)

        location = get_object_or_404(Location, id=location_id)

        # Anti-fraud check: 1 user can earn max 2 speedtests per location per day
        from django.utils import timezone
        from datetime import timedelta
        recent_count = InternetTest.objects.filter(
            location=location,
            user=request.user,
            created_at__gte=timezone.now() - timedelta(hours=12)
        ).count()

        ip = request.META.get('REMOTE_ADDR')
        test = InternetTest.objects.create(
            location=location,
            user=request.user,
            download_mbps=download_mbps,
            upload_mbps=upload_mbps,
            ping_ms=ping_ms,
            source='platform_speedtest',
            ip_address=ip
        )

        points_awarded = 0
        if recent_count < 2:
            request.user.add_points(10, f"{location.name} joyida Speedtest o‘tkazildi (+10 ball)", transaction_type='speedtest')
            points_awarded = 10

        return JsonResponse({
            'status': 'success',
            'message': f'Speedtest muvaffaqiyatli saqlandi! {points_awarded} ball qo‘shildi.',
            'points_awarded': points_awarded,
            'avg_download': location.avg_download_mbps,
            'avg_upload': location.avg_upload_mbps,
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
@csrf_exempt
def submit_noise_api(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST metodi talab qilinadi'}, status=405)
    
    try:
        data = json.loads(request.body)
        location_id = data.get('location_id')
        db_level = float(data.get('db_level', 0))
        duration_seconds = int(data.get('duration_seconds', 10))

        if not location_id or db_level <= 0:
            return JsonResponse({'status': 'error', 'message': 'Noto‘g‘ri ma’lumotlar'}, status=400)

        location = get_object_or_404(Location, id=location_id)

        NoiseTest.objects.create(
            location=location,
            user=request.user,
            db_level=db_level,
            duration_seconds=duration_seconds,
            source='decibel_meter'
        )

        return JsonResponse({
            'status': 'success',
            'message': 'Shovqin darajasi saqlandi!',
            'current_db': location.current_db_level
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def speedtest_tool_view(request):
    locations = Location.objects.filter(is_active=True).order_by('name')
    return render(request, 'measurements/speedtest_tool.html', {'locations': locations})
