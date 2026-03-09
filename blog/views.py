from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from .models import Post, Comment, Category
from .forms import PostForm
from .serializers import PostSerializer, CommentSerializer
from .pagination import CustomPageNumberPagination


# ===== ПРОВЕРКА ПРАВ =====
def is_admin(user):
    """Проверяет, является ли пользователь админом"""
    return user.is_staff or user.is_superuser


def check_limit(user):
    """Админ — безлимит, автор — 3 поста/день"""
    if user.is_staff or user.is_superuser:
        return True
    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    return Post.objects.filter(author=user, created_at__gte=today).count() < 3


# ===== HTML VIEW =====
def post_list(request):
    posts = Post.objects.select_related('author', 'category').all().order_by('-created_at')
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/post_list.html', {'page_obj': page_obj, 'paginator': paginator})


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
            return redirect('blog:post_detail', pk=post.pk)
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


# ===== КАТЕГОРИИ (ТОЛЬКО АДМИН) =====
@login_required
@user_passes_test(is_admin, login_url='blog:post_list')
def category_list(request):
    """Список категорий (только админ)"""
    categories = Category.objects.all().order_by('name')
    return render(request, 'blog/category_list.html', {'categories': categories})


@login_required
@user_passes_test(is_admin, login_url='blog:post_list')
def category_create(request):
    """Создание категории (только админ)"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            if Category.objects.filter(name__iexact=name).exists():
                messages.error(request, 'Категория с таким именем уже существует')
            else:
                Category.objects.create(name=name)
                messages.success(request, f'Категория "{name}" создана!')
                return redirect('blog:category_list')
        else:
            messages.error(request, 'Введите название категории')
    return render(request, 'blog/category_form.html')


@login_required
@user_passes_test(is_admin, login_url='blog:post_list')
def category_delete(request, pk):
    """Удаление категории (только админ)"""
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        category.delete()
        messages.success(request, f'Категория "{category.name}" удалена!')
        return redirect('blog:category_list')
    
    return render(request, 'blog/category_confirm_delete.html', {'category': category})


def login_view(request):
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('username'), 
                           password=request.POST.get('password'))
        if user:
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect('blog:post_list')
        messages.error(request, 'Неверные данные')
    return render(request, 'blog/login.html')


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Вы вышли из системы')
    return redirect('blog:post_list')


def register_view(request):
    if request.method == 'POST':
        if request.POST.get('password') != request.POST.get('password_confirm'):
            messages.error(request, 'Пароли не совпадают')
        elif User.objects.filter(username=request.POST.get('username')).exists():
            messages.error(request, 'Имя занято')
        else:
            User.objects.create_user(request.POST.get('username'), 
                                    password=request.POST.get('password'))
            messages.success(request, 'Аккаунт создан!')
            return redirect('blog:login')
    return render(request, 'blog/register.html')


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