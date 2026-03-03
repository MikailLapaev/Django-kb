from django.db import models
from django.contrib.auth.models import User

class Book(models.Model):
    title = models.CharField(max_length=100, verbose_name="Название")
    author = models.CharField(max_length=100, verbose_name="Автор")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='books', verbose_name="Владелец")

    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"
       
    def __str__(self):
        return self.title

    # Методы для проверки прав (аналог django-guardian) 
    def user_has_perm(self, user, perm):
        """Проверяет, есть ли у пользователя право на объект"""
        if perm == 'view_book':
            return user == self.owner or user.is_superuser
        return False