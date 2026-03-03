# books/serializers.py
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import Book
import re
import html

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['user_id'] = user.id
        token['username'] = user.username
        return token

class BookSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'owner']
    
    # ✅ Строгая валидация - запрещаем ВСЕ HTML-теги
    def validate_title(self, value):
        value = value.strip()
        
        # Проверка на наличие любых HTML-тегов
        if re.search(r'<[^>]+>', value):
            raise serializers.ValidationError("Название не должно содержать HTML-теги")
        
        # Проверка на JavaScript-протоколы
        if re.search(r'javascript:|vbscript:|data:', value, re.IGNORECASE):
            raise serializers.ValidationError("Недопустимый протокол в названии")
        
        # Проверка на спецсимволы для XSS
        if re.search(r'on\w+\s*=', value, re.IGNORECASE):  # onclick, onerror, onload и т.д.
            raise serializers.ValidationError("Название содержит недопустимые атрибуты")
        
        if len(value) < 1 or len(value) > 100:
            raise serializers.ValidationError("Название должно быть от 1 до 100 символов")
        
        return value
    
    def validate_author(self, value):
        value = value.strip()
        
        # Проверка на наличие любых HTML-тегов
        if re.search(r'<[^>]+>', value):
            raise serializers.ValidationError("Автор не должен содержать HTML-теги")
        
        # Проверка на JavaScript-протоколы
        if re.search(r'javascript:|vbscript:|data:', value, re.IGNORECASE):
            raise serializers.ValidationError("Недопустимый протокол в поле автор")
        
        # Проверка на спецсимволы для XSS
        if re.search(r'on\w+\s*=', value, re.IGNORECASE):
            raise serializers.ValidationError("Автор содержит недопустимые атрибуты")
        
        if len(value) < 1 or len(value) > 100:
            raise serializers.ValidationError("Автор должен быть от 1 до 100 символов")
        
        return value