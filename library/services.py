from django.core.cache import cache
from .models import Book

def get_books_by_genre_count():
    """Возвращает количество книг по жанрам с кэшированием (5 минут)."""
    cache_key = 'books_genre_count_v1'
    result = cache.get(cache_key)
    
    if result is None:
        print("⚠️ [КЭШ] Вычисляем количество книг по жанрам...")
        result = {}
        for genre_code, genre_name in Book.GENRE_CHOICES:
            count = Book.objects.filter(genre=genre_code).count()
            result[genre_name] = count
        cache.set(cache_key, result, 300)
    else:
        print("[КЭШ] Данные о жанрах взяты из кэша!")
    
    return result


def clear_books_cache():
    """Очищает кэш при изменении данных"""
    cache.delete('books_genre_count_v1')