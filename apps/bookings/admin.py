from django.contrib import admin
from .models import Booking, CheckIn


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_code', 'user', 'location', 'zone', 'table', 'booking_date', 'start_time', 'end_time', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'booking_date', 'location')
    search_fields = ('booking_code', 'user__username', 'location__name')


@admin.register(CheckIn)
class CheckInAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'booking', 'method', 'is_verified', 'created_at')
    list_filter = ('method', 'is_verified')
    search_fields = ('user__username', 'location__name', 'check_in_code')
