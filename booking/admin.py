from django.contrib import admin
from .models import Category

@admin.register(Category)
class BookingAdmin(admin.ModelAdmin):
    def get_location(self, obj):
        from .models import BlogPost  # inline import
        return obj.location.name