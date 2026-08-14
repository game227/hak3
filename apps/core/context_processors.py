from apps.core.models import Notification
from apps.locations.models import Location


def global_context(request):
    unread_notifications_count = 0
    if request.user.is_authenticated:
        unread_notifications_count = Notification.objects.filter(user=request.user, is_read=False).count()

    return {
        'SITE_NAME': 'QuietSpace Tashkent',
        'SITE_TAGLINE': 'Shahar ichidagi tinch va masofaviy ishlash joylari ekotizimi',
        'unread_notifications_count': unread_notifications_count,
        'TOTAL_SPACES_COUNT': Location.objects.filter(is_active=True).count(),
    }
