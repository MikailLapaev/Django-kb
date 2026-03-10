from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Book, Genre, UserProfile, Role
from .forms import BookForm, CustomUserCreationForm, GenreForm


def home(request):
    """Главная страница с пагинацией"""
    total_books = Book.objects.count()
    total_authors = Book.objects.values('author').distinct().count()
    total_genres = Genre.objects.count()
    total_users = User.objects.count()
    
    # Пагинация для книг на главной
    books_list = Book.objects.select_related('genre', 'owner').all()
    paginator = Paginator(books_list, 6)  # 6 книг на странице
    page_number = request.GET.get('page')
    recent_books = paginator.get_page(page_number)
    
    is_admin = False
    if request.user.is_authenticated:
        try:
            is_admin = request.user.profile.is_admin()
        except:
            is_admin = request.user.is_superuser
    
    context = {
        'total_books': total_books,
        'total_authors': total_authors,
        'total_genres': total_genres,
        'total_users': total_users,
        'recent_books': recent_books,
        'is_admin': is_admin,
        'has_books': books_list.exists(),
        'page_obj': recent_books,
    }
    
    return render(request, 'home.html', context)


class BookListView(ListView):
    model = Book
    template_name = 'books/book_list.html'
    context_object_name = 'books'
    paginate_by = 6

    def get_queryset(self):
        return Book.objects.select_related('genre')


class BookDetailView(DetailView):
    model = Book
    template_name = 'books/book_detail.html'
    context_object_name = 'book'


class BookCreateView(LoginRequiredMixin, CreateView):
    model = Book
    form_class = BookForm
    template_name = 'books/book_form.html'
    success_url = reverse_lazy('book_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class BookUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Book
    form_class = BookForm
    template_name = 'books/book_form.html'
    success_url = reverse_lazy('book_list')

    def test_func(self):
        book = self.get_object()
        return self.request.user == book.owner or self.request.user.is_superuser


class BookDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Book
    template_name = 'books/book_confirm_delete.html'
    success_url = reverse_lazy('book_list')

    def test_func(self):
        book = self.get_object()
        return self.request.user == book.owner or self.request.user.is_superuser


class GenreListView(LoginRequiredMixin, ListView):
    model = Genre
    template_name = 'books/genre_list.html'
    context_object_name = 'genres'
    ordering = ['name']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_admin'] = self.request.user.is_superuser or (
            hasattr(self.request.user, 'profile') and 
            self.request.user.profile.is_admin()
        )
        return context


class GenreCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Genre
    form_class = GenreForm
    template_name = 'books/genre_form.html'
    success_url = reverse_lazy('genre_list')
    
    def test_func(self):
        return self.request.user.is_superuser or (
            hasattr(self.request.user, 'profile') and 
            self.request.user.profile.is_admin()
        )
    
    def form_valid(self, form):
        messages.success(self.request, f'Жанр "{form.instance.name}" успешно создан!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавить жанр'
        return context


class GenreUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Genre
    form_class = GenreForm
    template_name = 'books/genre_form.html'
    success_url = reverse_lazy('genre_list')
    
    def test_func(self):
        return self.request.user.is_superuser or (
            hasattr(self.request.user, 'profile') and 
            self.request.user.profile.is_admin()
        )
    
    def form_valid(self, form):
        messages.success(self.request, f'Жанр "{form.instance.name}" успешно обновлён!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактировать жанр'
        return context


class GenreDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Genre
    template_name = 'books/genre_confirm_delete.html'
    success_url = reverse_lazy('genre_list')
    
    def test_func(self):
        return self.request.user.is_superuser or (
            hasattr(self.request.user, 'profile') and 
            self.request.user.profile.is_admin()
        )
    
    def delete(self, request, *args, **kwargs):
        genre_name = self.get_object().name
        messages.success(request, f'Жанр "{genre_name}" успешно удалён!')
        return super().delete(request, *args, **kwargs)


class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'


class CustomLogoutView(LogoutView):
    template_name = 'registration/logout.html'