"""
URL configuration for QuietSpace Tashkent.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('measurements/', include('apps.measurements.urls')),
    path('ai/', include('apps.ai_service.urls')),
    path('b2b/', include('apps.b2b.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = "QuietSpace Tashkent Boshqaruv Paneli"
admin.site.site_title = "QuietSpace Admin"
admin.site.index_title = "Platforma Boshqaruvi"
