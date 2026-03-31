from django.urls import path
from .views import BookListView

app_name = 'library'

urlpatterns = [
    path('books/', BookListView.as_view(), name='book_list'),
]