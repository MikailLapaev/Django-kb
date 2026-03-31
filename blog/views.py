# blog/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Post, Comment, Category, LoginAttempt
from .forms import PostForm, CommentForm, CategoryForm, RegistrationForm, LoginForm
from .serializers import PostSerializer, CommentSerializer, CategorySerializer, UserRegistrationSerializer, UserSerializer
from .pagination import CustomPageNumberPagination
from .validators import check_login_attempts, log_login_attempt
from django.views.decorators.cache import cache_page


# ===== ПРОВЕРКА ПРАВ =====
def is_admin(user):
    return user.is_staff or user.is_superuser


def check_limit(user):
    if user.is_staff or user.is_superuser:
        return True
    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    return Post.objects.filter(author=user, created_at__gte=today).count() < 3


# ===== ФУНКЦИИ ДЛЯ КЭШИРОВАНИЯ =====

def get_blog_stats():
    """
    Получает статистику блога с кэшированием.
    Данные обновляются раз в 5 минут.
    """
    from django.core.cache import cache
    
    cache_key = 'blog_stats_v1'  # Уникальный ключ
    stats = cache.get(cache_key)
    
    if stats is None:
        # Если нет в кэше — считаем (тяжёлая операция)
        print("Вычисляем статистику заново...")
        
        stats = {
            'total_posts': Post.objects.count(),
            'total_comments': Comment.objects.count(),
            'total_categories': Category.objects.count(),
            'recent_posts_count': Post.objects.filter(
                created_at__gte=timezone.now() - timezone.timedelta(days=7)
            ).count(),
        }
        
        # Сохраняем в кэш на 5 минут (300 секунд)
        cache.set(cache_key, stats, 300)
    else:
        print("Статистика взята из кэша!")
    
    return stats


# ===== HTML VIEW =====
@cache_page(60)  #Кэшируем на 60 секунд
def post_list(request):
    posts = Post.objects.select_related('author', 'category').all().order_by('-created_at')
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/post_list.html', {
        'page_obj': page_obj, 
        'paginator': paginator,
        'cache_time': timezone.now(),  # Для отладки: время генерации
        'stats': get_blog_stats()
    })



def post_detail(request, pk):
    post = get_object_or_404(Post.objects.select_related('author', 'category'), pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})




@login_required
def post_create(request):
    if not check_limit(request.user):
        messages.error(request, 'Лимит: 3 поста в день')
        return redirect('blog:post_list')
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Пост создан!')
            return redirect('blog:post_detail', pk=post.pk)
        else:
            messages.error(request, 'Исправьте ошибки в форме.')
    else:
        form = PostForm()
    is_admin_user = request.user.is_staff or request.user.is_superuser
    return render(request, 'blog/post_form.html', {'form': form, 'is_admin': is_admin_user})


@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user and not request.user.is_staff:
        messages.error(request, 'Нет прав')
        return redirect('blog:post_detail', pk=pk)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Пост обновлён!')
            return redirect('blog:post_detail', pk=post.pk)
        else:
            messages.error(request, 'Исправьте ошибки в форме.')
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_form.html', {'form': form})


@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user and not request.user.is_staff:
        messages.error(request, 'Нет прав')
        return redirect('blog:post_detail', pk=pk)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Пост удалён!')
        return redirect('blog:post_list')
    return render(request, 'blog/post_confirm_delete.html', {'post': post})


@login_required
@user_passes_test(is_admin, login_url='blog:post_list')
def category_list(request):
    categories = Category.objects.all().order_by('name')
    return render(request, 'blog/category_list.html', {'categories': categories})


@login_required
@user_passes_test(is_admin, login_url='blog:post_list')
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Категория "{form.cleaned_data["name"]}" создана!')
            return redirect('blog:category_list')
        else:
            messages.error(request, 'Исправьте ошибки в форме.')
    else:
        form = CategoryForm()
    return render(request, 'blog/category_form.html', {'form': form})


@login_required
@user_passes_test(is_admin, login_url='blog:post_list')
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, f'Категория "{category.name}" удалена!')
        return redirect('blog:category_list')
    return render(request, 'blog/category_confirm_delete.html', {'category': category})
# blog/views.py
@login_required
@user_passes_test(is_admin, login_url='blog:post_list')
def category_list(request):
    categories = Category.objects.all().order_by('name')
    return render(request, 'blog/category_list.html', {
        'categories': categories,
        'stats': get_blog_stats(), 
    })


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            if not check_login_attempts(username):
                messages.error(request, 'Слишком много неудачных попыток. Попробуйте через 15 минут.')
                return render(request, 'blog/login.html', {'form': form})
            
            user = authenticate(request, username=username, password=password)
            
            if user:
                login(request, user)
                log_login_attempt(username, True, request.META.get('REMOTE_ADDR'))
                messages.success(request, f'Добро пожаловать, {user.username}!')
                return redirect('blog:post_list')
            else:
                log_login_attempt(username, False, request.META.get('REMOTE_ADDR'))
                messages.error(request, 'Неверное имя пользователя или пароль.')
        else:
            messages.error(request, 'Исправьте ошибки в форме.')
    else:
        form = LoginForm()
    return render(request, 'blog/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Вы вышли из системы')
    return redirect('blog:post_list')


def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data.get('first_name', '')
            )
            messages.success(request, 'Аккаунт создан! Теперь вы можете войти.')
            return redirect('blog:login')
        else:
            messages.error(request, 'Исправьте ошибки в форме.')
    else:
        form = RegistrationForm()
    return render(request, 'blog/register.html', {'form': form})


# ===== API VIEWSET =====
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    pagination_class = CustomPageNumberPagination
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [IsAuthenticated()]
        return [AllowAny()]

    def perform_create(self, serializer):
        if not check_limit(self.request.user):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Лимит: 3 поста в день')
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('-created_at')
    serializer_class = CommentSerializer
    pagination_class = CustomPageNumberPagination
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [IsAuthenticated()]
        return [AllowAny()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    pagination_class = CustomPageNumberPagination
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [IsAuthenticated()]
        return [AllowAny()]