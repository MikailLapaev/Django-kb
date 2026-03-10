from django.db import models
from django.contrib.auth.models import User

class Role(models.Model):
    """Модель ролей пользователей"""
    name = models.CharField('Название роли', max_length=50, unique=True)
    description = models.TextField('Описание', blank=True)
    is_admin = models.BooleanField('Администратор', default=False)
    
    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'
    
    def __str__(self):
        return self.name

class UserProfile(models.Model):
    """Расширенный профиль пользователя"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Роль')
    avatar = models.ImageField('Аватар', upload_to='avatars/', blank=True, null=True)
    bio = models.TextField('О себе', blank=True)
    created_at = models.DateTimeField('Дата регистрации', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'
    
    def __str__(self):
        return f'{self.user.username} ({self.role.name if self.role else "Без роли"})'
    
    def is_admin(self):
        """Проверка на администратора"""
        return self.role and self.role.is_admin

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

class Book(models.Model):
    title = models.CharField('Название', max_length=200)
    author = models.CharField('Автор', max_length=100)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, related_name='books', verbose_name='Жанр')
    description = models.TextField('Описание', blank=True, null=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Владелец')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'
    
    def __str__(self):
        return f"{self.title} ({self.author})"