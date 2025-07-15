from rest_framework import serializers
from hiking.models import Category, Location, Tour, TourDate, Booking, Review
from django.contrib.auth.models import User

class CategorySerializer(serializers.ModelSerializer):
    tours_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'tours_count', 'created_at']
    
    def get_tours_count(self, obj):
        return obj.tours.filter(active=True).count()

class LocationSerializer(serializers.ModelSerializer):
    tours_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Location
        fields = ['id', 'name', 'country', 'state', 'city', 'latitude', 'longitude', 
                 'description', 'tours_count', 'created_at']
    
    def get_tours_count(self, obj):
        return obj.tours.filter(active=True).count()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class TourDateSerializer(serializers.ModelSerializer):
    guide = UserSerializer(read_only=True)
    
    class Meta:
        model = TourDate
        fields = ['id', 'start_date', 'end_date', 'available_spots', 'guide', 'created_at']

class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'user', 'rating', 'comment', 'created_at']
        read_only_fields = ['user']

class TourSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    location = LocationSerializer(read_only=True)
    dates = TourDateSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Tour
        fields = ['id', 'title', 'description', 'category', 'location', 'duration_days',
                 'difficulty', 'price', 'max_participants', 'image', 'featured', 'active',
                 'dates', 'reviews', 'average_rating', 'reviews_count', 'created_at', 'updated_at']
    
    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0
    
    def get_reviews_count(self, obj):
        return obj.reviews.count()

class BookingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    tour_date = TourDateSerializer(read_only=True)
    tour_date_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Booking
        fields = ['id', 'user', 'tour_date', 'tour_date_id', 'participants', 'total_price',
                 'status', 'booking_reference', 'created_at', 'updated_at']
        read_only_fields = ['user', 'booking_reference', 'total_price']