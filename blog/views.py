from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework import viewsets
from .models import Post, Category, Comment
from .forms import PostForm
from .serializers import PostSerializer, CommentSerializer
from .pagination import CustomPageNumberPagination, CustomLimitOffsetPagination


# ==================== ФУНКЦИОННЫЕ VIEW (для HTML шаблонов) ====================

def post_list(request):
    posts = Post.objects.all().select_related('author', 'category').order_by('-created_at')
    
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    context = {
        'page_obj': page_obj,
        'paginator': paginator,
        'posts': page_obj
    }
    
    return render(request, 'blog/post_list.html', context)


def post_detail(request, pk):
    post = get_object_or_404(Post.objects.select_related('author', 'category'), pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            posts_count = Post.objects.filter(
                author=request.user, 
                created_at__gte=today_start
            ).count()
            
            if posts_count >= 3:
                messages.error(request, 'Вы превысили дневной лимит публикаций (3 поста в день)')
                return redirect('blog:post_create')
            
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Пост успешно создан!')
            return redirect('blog:post_detail', pk=post.pk)
    else:
        form = PostForm()
    
    return render(request, 'blog/post_form.html', {'form': form})


@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    # Проверка прав: владелец ИЛИ модератор категории ИЛИ админ/суперпользователь
    can_edit = (
        post.author == request.user or 
        request.user in post.category.moderators.all() or
        request.user.is_staff or
        request.user.is_superuser
    )
    
    if not can_edit:
        raise PermissionDenied()
    
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Пост успешно обновлён!')
            return redirect('blog:post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    
    return render(request, 'blog/post_form.html', {'form': form, 'post': post})


@login_required
def post_delete(request, pk):
    """
    Удаление поста с проверкой прав:
    - Админ/суперпользователь может удалить ЛЮБОЙ пост
    - Автор может удалить СВОЙ пост
    - Модератор категории может удалить посты в своей категории
    """
    post = get_object_or_404(Post, pk=pk)
    
    # Проверка прав на удаление
    can_delete = (
        request.user.is_superuser or           # Суперпользователь
        request.user.is_staff or               # Админ (staff)
        post.author == request.user or         # Автор поста
        request.user in post.category.moderators.all()  # Модератор категории
    )
    
    if not can_delete:
        raise PermissionDenied()
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Пост успешно удалён!')
        return redirect('blog:post_list')
    
    # GET-запрос — показываем страницу подтверждения
    return render(request, 'blog/post_confirm_delete.html', {'post': post})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect('blog:post_list')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')
    
    return render(request, 'blog/login.html')


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Вы вышли из системы')
    return redirect('blog:post_list')


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        if password != password_confirm:
            messages.error(request, 'Пароли не совпадают')
            return render(request, 'blog/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь с таким именем уже существует')
            return render(request, 'blog/register.html')
        
        user = User.objects.create_user(username=username, password=password)
        messages.success(request, f'Аккаунт {username} создан! Теперь вы можете войти.')
        return redirect('blog:login')
    
    return render(request, 'blog/register.html')


# ==================== API VIEWSETS (для REST API) ====================

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    pagination_class = CustomPageNumberPagination


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('-created_at')
    serializer_class = CommentSerializer
    pagination_class = CustomLimitOffsetPagination