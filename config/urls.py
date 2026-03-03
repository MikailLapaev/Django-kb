from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from books.views import BookListCreateView, BookDetailView, login_view, books_view, check_auth

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # JWT API
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Books API
    path('books/', BookListCreateView.as_view(), name='books-list-create'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='books-detail'),
    path('api/check-auth/', check_auth, name='check-auth'),
    
    # Frontend Pages
    path('login/', login_view, name='login'),
    path('books-page/', books_view, name='books-page'),
    path('', login_view, name='home'),
]