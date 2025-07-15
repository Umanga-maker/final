from django.shortcuts import render

# Create your views here.
from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound, ValidationError
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from .models import BlogPost, Category
from serializer.booking_serializers import (
    BlogPostListSerializer, 
    BlogPostDetailSerializer,
    BlogPostCreateSerializer,
    CategorySerializer
)
import logging

logger = logging.getLogger(__name__)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class BlogPostListView(generics.ListAPIView):
    serializer_class = BlogPostListSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'author']
    search_fields = ['title', 'content', 'excerpt']
    ordering_fields = ['created_at', 'views', 'title']
    ordering = ['-created_at']
    
    def get_queryset(self):
        try:
            queryset = BlogPost.objects.filter(is_published=True).select_related('author', 'category')
            return queryset
        except Exception as e:
            logger.error(f"Error in BlogPostListView: {e}")
            raise ValidationError("Error retrieving blog posts")

class BlogPostDetailView(generics.RetrieveAPIView):
    serializer_class = BlogPostDetailSerializer
    lookup_field = 'slug'
    
    def get_object(self):
        try:
            slug = self.kwargs.get('slug')
            obj = get_object_or_404(BlogPost, slug=slug, is_published=True)
            
            # Increment view count
            obj.views += 1
            obj.save(update_fields=['views'])
            
            return obj
        except Http404:
            raise NotFound("Blog post not found")
        except Exception as e:
            logger.error(f"Error in BlogPostDetailView: {e}")
            raise ValidationError("Error retrieving blog post")

class BlogPostCreateView(generics.CreateAPIView):
    serializer_class = BlogPostCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        try:
            serializer.save(author=self.request.user)
        except Exception as e:
            logger.error(f"Error creating blog post: {e}")
            raise ValidationError("Error creating blog post")

class BlogPostUpdateView(generics.UpdateAPIView):
    serializer_class = BlogPostCreateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'
    
    def get_queryset(self):
        return BlogPost.objects.filter(author=self.request.user)
    
    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            raise NotFound("Blog post not found or you don't have permission to edit it")

class BlogPostDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'
    
    def get_queryset(self):
        return BlogPost.objects.filter(author=self.request.user)
    
    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            raise NotFound("Blog post not found or you don't have permission to delete it")

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
    def get_queryset(self):
        try:
            return Category.objects.all()
        except Exception as e:
            logger.error(f"Error in CategoryListView: {e}")
            raise ValidationError("Error retrieving categories")

@api_view(['GET'])
def blog_stats(request):
    """
    Get blog statistics
    """
    try:
        stats = {
            'total_posts': BlogPost.objects.filter(is_published=True).count(),
            'total_categories': Category.objects.count(),
            'total_views': sum(BlogPost.objects.filter(is_published=True).values_list('views', flat=True)),
        }
        return Response({
            'error': False,
            'message': 'Blog statistics retrieved successfully',
            'data': stats
        })
    except Exception as e:
        logger.error(f"Error getting blog stats: {e}")
        return Response({
            'error': True,
            'message': 'Error retrieving blog statistics'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def search_posts(request):
    """
    Search blog posts
    """
    try:
        query = request.GET.get('q', '')
        if not query:
            return Response({
                'error': True,
                'message': 'Search query is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        posts = BlogPost.objects.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) | 
            Q(excerpt__icontains=query),
            is_published=True
        )
        
        serializer = BlogPostListSerializer(posts, many=True)
        return Response({
            'error': False,
            'message': 'Search completed successfully',
            'data': serializer.data,
            'count': posts.count()
        })
    except Exception as e:
        logger.error(f"Error in search: {e}")
        return Response({
            'error': True,
            'message': 'Error performing search'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
