from rest_framework import permissions
from django.utils import timezone
from .models import Post

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешает редактирование/удаление только автору объекта.
    Чтение доступно всем (или аутентифицированным, в зависимости от View).
    """
    def has_object_permission(self, request, view, obj):
        # Безопасные методы (GET, HEAD, OPTIONS) разрешены
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Проверка авторства
        return obj.author == request.user

class IsModerator(permissions.BasePermission):
    """
    Проверяет, является ли пользователь модератором категории объекта.
    """
    def has_object_permission(self, request, view, obj):
        # obj должен иметь атрибут category
        if hasattr(obj, 'category'):
            return request.user in obj.category.moderators.all()
        return False

    def has_permission(self, request, view):
        # Для создания (POST) проверяем категорию из данных
        if request.method == 'POST':
            category_id = request.data.get('category')
            if category_id:
                try:
                    from .models import Category
                    category = Category.objects.get(pk=category_id)
                    return request.user in category.moderators.all()
                except (Category.DoesNotExist, ValueError):
                    return False
        return True

class DailyPostLimit(permissions.BasePermission):
    """
    Ограничивает создание постов: не более N постов в сутки для одного пользователя.
    """
    message = "Вы превысили дневной лимит публикаций."
    limit = 3  # Установим лимит в 3 поста для теста

    def has_permission(self, request, view):
        # Проверяем только при создании
        if request.method != 'POST':
            return True
        
        if not request.user.is_authenticated:
            return False

        # Начало текущих суток
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Подсчет постов
        count = Post.objects.filter(author=request.user, created_at__gte=today_start).count()
        
        return count < self.limit

class IsOwnerOrModerator(permissions.BasePermission):
    """
    Комбинированное разрешение: Доступ разрешен, если пользователь 
    является автором объекта ИЛИ модератором категории.
    Нужно для редактирования/удаления.
    """
    def has_object_permission(self, request, view, obj):
        is_owner = obj.author == request.user
        is_moderator = False
        
        if hasattr(obj, 'category'):
            is_moderator = request.user in obj.category.moderators.all()
            
        return is_owner or is_moderator