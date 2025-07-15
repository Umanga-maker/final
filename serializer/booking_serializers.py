from rest_framework import serializers
from booking.models import BlogPost, Category
from django.contrib.auth.models import User

class CategorySerializer(serializers.ModelSerializer):
    post_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'post_count']
    
    def get_post_count(self, obj):
        return obj.blogpost_set.filter(is_published=True).count()

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']

class BlogPostListSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    
    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'slug', 'author', 'category', 'excerpt', 
                 'image', 'created_at', 'views']

class BlogPostDetailSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    
    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'slug', 'author', 'category', 'content', 
                 'excerpt', 'image', 'created_at', 'updated_at', 'views']

class BlogPostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = ['title', 'slug', 'category', 'content', 'excerpt', 
                 'image', 'is_published']
    
    def validate_slug(self, value):
        if BlogPost.objects.filter(slug=value).exists():
            raise serializers.ValidationError("A post with this slug already exists.")
        return value