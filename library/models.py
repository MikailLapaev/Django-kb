from django.db import models

class Book(models.Model):
    GENRE_CHOICES = [
        ('fiction', '📖 Художественная'),
        ('science', '🔬 Научная'),
        ('history', '📜 История'),
        ('tech', '💻 Технологии'),
        ('other', '📚 Другое'),
    ]
    
    title = models.CharField('Название', max_length=200)
    author = models.CharField('Автор', max_length=100)
    genre = models.CharField('Жанр', max_length=20, choices=GENRE_CHOICES, default='other')
    created_at = models.DateTimeField('Дата добавления', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.title} ({self.author})'