from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('explore/', views.explore_map_view, name='explore_map'),
    path('locations/<slug:slug>/', views.location_detail_view, name='location_detail'),
    path('location/<slug:slug>/', views.location_detail_view, name='location_detail_alias'),
    path('locations/<int:location_id>/book/', views.create_booking_view, name='create_booking'),
    path('locations/<int:location_id>/review/', views.submit_review_view, name='submit_review'),
    path('checkout/booking/<int:booking_id>/', views.checkout_booking_view, name='checkout_booking'),
    path('my-bookings/', views.my_bookings_view, name='my_bookings'),
    path('bookings/<int:booking_id>/cancel/', views.cancel_booking_view, name='cancel_booking'),
    path('quietpass/', views.quietpass_view, name='quietpass'),
    path('quietpass/buy/<int:plan_id>/', views.buy_quietpass_view, name='buy_quietpass'),
    path('notifications/', views.notifications_view, name='notifications'),
    
    # Admin Payment Management
    path('admin-panel/payments/', views.admin_payment_management_view, name='admin_payments'),
    path('admin-panel/payments/<int:payment_id>/action/', views.admin_payment_action_view, name='admin_payment_action'),
    path('admin-panel/audits/', views.admin_audit_log_view, name='admin_audits'),
]
