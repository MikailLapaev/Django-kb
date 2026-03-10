from django.urls import path
from .views import (
    home,
    BookListView, BookDetailView, BookCreateView, 
    BookUpdateView, BookDeleteView, RegisterView, 
    CustomLoginView, CustomLogoutView,
    GenreListView, GenreCreateView, GenreUpdateView, GenreDeleteView
)

urlpatterns = [
    path('', home, name='home'),
    path('books/', BookListView.as_view(), name='book_list'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='book_detail'),
    path('books/create/', BookCreateView.as_view(), name='book_create'),
    path('books/<int:pk>/update/', BookUpdateView.as_view(), name='book_update'),
    path('books/<int:pk>/delete/', BookDeleteView.as_view(), name='book_delete'),
    
    # Жанры
    path('genres/', GenreListView.as_view(), name='genre_list'),
    path('genres/create/', GenreCreateView.as_view(), name='genre_create'),
    path('genres/<int:pk>/update/', GenreUpdateView.as_view(), name='genre_update'),
    path('genres/<int:pk>/delete/', GenreDeleteView.as_view(), name='genre_delete'),
    
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
]