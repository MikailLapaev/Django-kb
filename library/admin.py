from django.contrib import admin
from .models import Book

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'genre', 'created_at']
    list_filter = ['genre', 'created_at']
    search_fields = ['title', 'author']
    list_per_page = 20