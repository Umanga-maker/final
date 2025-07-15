from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Avg
from .models import Category, Location, Tour, TourDate, Booking, Review
from serializer.hiking_serializers import (CategorySerializer, LocationSerializer, TourSerializer,
                         TourDateSerializer, BookingSerializer, ReviewSerializer)
import uuid

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'country', 'state', 'city']
    filterset_fields = ['country', 'state']

class TourViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tour.objects.filter(active=True)
    serializer_class = TourSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['title', 'description', 'location__name', 'category__name']
    filterset_fields = ['category', 'location', 'difficulty', 'featured']
    ordering_fields = ['price', 'duration_days', 'created_at']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured tours"""
        featured_tours = self.queryset.filter(featured=True)
        serializer = self.get_serializer(featured_tours, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Advanced search with filters"""
        queryset = self.queryset
        
        # Filter by price range
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Filter by duration
        min_duration = request.query_params.get('min_duration')
        max_duration = request.query_params.get('max_duration')
        if min_duration:
            queryset = queryset.filter(duration_days__gte=min_duration)
        if max_duration:
            queryset = queryset.filter(duration_days__lte=max_duration)
        
        # Filter by availability
        available_only = request.query_params.get('available_only', 'false').lower() == 'true'
        if available_only:
            queryset = queryset.filter(dates__available_spots__gt=0).distinct()
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class TourDateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TourDate.objects.all()
    serializer_class = TourDateSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['tour', 'guide']
    ordering_fields = ['start_date', 'end_date']
    ordering = ['start_date']
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get available tour dates"""
        available_dates = self.queryset.filter(available_spots__gt=0)
        serializer = self.get_serializer(available_dates, many=True)
        return Response(serializer.data)

class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'tour_date__tour']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # Generate booking reference
        booking_ref = str(uuid.uuid4())[:8].upper()
        
        # Calculate total price
        tour_date = serializer.validated_data['tour_date_id']
        tour_date_obj = TourDate.objects.get(id=tour_date)
        participants = serializer.validated_data['participants']
        total_price = tour_date_obj.tour.price * participants
        
        serializer.save(
            user=self.request.user,
            booking_reference=booking_ref,
            total_price=total_price,
            tour_date=tour_date_obj
        )
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a booking"""
        booking = self.get_object()
        if booking.status == 'pending':
            booking.status = 'cancelled'
            booking.save()
            return Response({'message': 'Booking cancelled successfully'})
        return Response({'error': 'Cannot cancel this booking'}, 
                       status=status.HTTP_400_BAD_REQUEST)

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['tour', 'rating']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action in ['update', 'partial_update', 'destroy']:
            return queryset.filter(user=self.request.user)
        return queryset
