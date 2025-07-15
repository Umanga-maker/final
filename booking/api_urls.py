from django.urls import path, include
from . import views

urlpatterns = [
    
    # Blog posts
    path('posts/', views.BlogPostListView.as_view(), name='blog-post-list'),
    path('posts/<slug:slug>/', views.BlogPostDetailView.as_view(), name='blog-post-detail'),
    path('posts/create/', views.BlogPostCreateView.as_view(), name='blog-post-create'),
    path('posts/<slug:slug>/update/', views.BlogPostUpdateView.as_view(), name='blog-post-update'),
    path('posts/<slug:slug>/delete/', views.BlogPostDeleteView.as_view(), name='blog-post-delete'),
    
    # Categories
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    
    # Utilities
    path('stats/', views.blog_stats, name='blog-stats'),
    path('search/', views.search_posts, name='search-posts'),
]

# settings.py (add these to your Django settings)
"""
INSTALLED_APPS = [
    # ... other apps
    'rest_framework',
    'django_filters',
    'corsheaders',  # for CORS if needed
    'banners',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'EXCEPTION_HANDLER': 'your_app.exceptions.custom_exception_handler',
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': 'blog_api_errors.log',
        },
    },
    'loggers': {
        'your_app': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
"""
