from django.urls import path
from . import views

app_name = 'measurements'

urlpatterns = [
    path('speedtest/', views.speedtest_tool_view, name='speedtest'),
    path('tool/', views.speedtest_tool_view, name='speedtest_tool'),
    path('api/submit-speedtest/', views.submit_speedtest_api, name='submit_speedtest_api'),
    path('api/submit-noise/', views.submit_noise_api, name='submit_noise_api'),
]
