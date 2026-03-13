# blog/serializers.py
from rest_framework import serializers
from .models import Post, Comment, Category
from django.contrib.auth.models import User
from .validators import (
    sanitize_input, validate_forbidden_patterns,
    validate_password_strength, validate_email_domain,
    validate_username_business_rule, validate_first_name_cyrillic,
    validate_post_title, validate_post_content, validate_comment_content,
    validate_category_name
)


class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'category', 'created_at']
        read_only_fields = ['author', 'created_at']
    
    def validate_title(self, value):
        value = sanitize_input(value)
        validate_forbidden_patterns(value, 'Заголовок')
        validate_post_title(value)
        return value
    
    def validate_content(self, value):
        value = sanitize_input(value)
        validate_forbidden_patterns(value, 'Содержание')
        validate_post_content(value)
        return value


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    
    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'created_at']
        read_only_fields = ['author', 'created_at']
    
    def validate_content(self, value):
        value = sanitize_input(value)
        validate_forbidden_patterns(value, 'Комментарий')
        validate_comment_content(value)
        return value


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']
    
    def validate_name(self, value):
        value = sanitize_input(value)
        validate_forbidden_patterns(value, 'Название категории')
        validate_category_name(value)
        return value


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'text'})
    password_confirm = serializers.CharField(write_only=True, style={'input_type': 'text'})
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']
    
    def validate_username(self, value):
        value = sanitize_input(value)
        validate_forbidden_patterns(value, 'Имя пользователя')
        validate_username_business_rule(value)
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError('Пользователь с таким именем уже существует.')
        return value
    
    def validate_email(self, value):
        value = sanitize_input(value)
        validate_email_domain(value)
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('Email уже зарегистрирован.')
        return value
    
    def validate_password(self, value):
        validate_password_strength(value)
        return value
    
    def validate_first_name(self, value):
        if value:
            value = sanitize_input(value)
            validate_first_name_cyrillic(value)
        return value
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Пароли не совпадают.'})
        if 'test' in data['username'].lower() and not data.get('first_name'):
            raise serializers.ValidationError({'first_name': 'Для тестовых аккаунтов необходимо указать имя.'})
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user