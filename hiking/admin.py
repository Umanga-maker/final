from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib import admin
from .models import Category, Location, Tour, TourDate, Booking, Review

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'state', 'city', 'created_at']
    list_filter = ['country', 'state']
    search_fields = ['name', 'country', 'city']

@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'location', 'difficulty', 'price', 'featured', 'active']
    list_filter = ['category', 'difficulty', 'featured', 'active', 'created_at']
    search_fields = ['title', 'description']
    list_editable = ['featured', 'active']

@admin.register(TourDate)
class TourDateAdmin(admin.ModelAdmin):
    list_display = ['tour', 'start_date', 'end_date', 'available_spots', 'guide']
    list_filter = ['start_date', 'tour__category']
    search_fields = ['tour__title']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_reference', 'user', 'tour_date', 'participants', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['booking_reference', 'user__username']
    readonly_fields = ['booking_reference', 'total_price']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['tour', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['tour__title', 'user__username']