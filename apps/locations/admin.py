from django.contrib import admin
from .models import Business, Amenity, Location, LocationImage, Zone, TableDesk


class LocationImageInline(admin.TabularInline):
    model = LocationImage
    extra = 1


class ZoneInline(admin.TabularInline):
    model = Zone
    extra = 1


class TableDeskInline(admin.TabularInline):
    model = TableDesk
    extra = 2


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('brand_name', 'name', 'owner', 'phone', 'is_verified', 'created_at')
    list_filter = ('is_verified',)
    search_fields = ('name', 'brand_name', 'owner__username', 'phone')


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'category', 'icon')
    list_filter = ('category',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'district', 'category', 'live_status', 'current_db_level', 'avg_download_mbps', 'hourly_price', 'rating', 'is_promoted', 'is_verified')
    list_filter = ('district', 'category', 'live_status', 'is_promoted', 'is_verified', 'is_active')
    search_fields = ('name', 'address', 'district', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [LocationImageInline, ZoneInline]


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'zone_type', 'noise_level_expected', 'capacity')
    list_filter = ('zone_type', 'noise_level_expected')
    search_fields = ('name', 'location__name')
    inlines = [TableDeskInline]


@admin.register(TableDesk)
class TableDeskAdmin(admin.ModelAdmin):
    list_display = ('table_number', 'zone', 'has_outlet', 'hourly_price', 'is_active')
    list_filter = ('has_outlet', 'is_active')
    search_fields = ('table_number', 'zone__name', 'zone__location__name')
