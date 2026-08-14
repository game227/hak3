from django.urls import path
from . import views

app_name = 'b2b'

urlpatterns = [
    path('', views.b2b_dashboard, name='dashboard'),
    path('dashboard/', views.b2b_dashboard, name='dashboard_alias'),
    path('live-status/<int:location_id>/', views.b2b_set_live_status, name='set_live_status'),
    path('checkin/', views.b2b_verify_checkin, name='checkin'),
    path('bookings/', views.b2b_bookings_list, name='bookings_list'),
    path('inventory/<int:location_id>/', views.b2b_inventory, name='inventory'),
    path('promotions/', views.b2b_promotions, name='promotions'),
]
