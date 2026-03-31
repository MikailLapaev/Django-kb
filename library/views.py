from django.views.generic import ListView
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from .models import Book
from .services import get_books_by_genre_count


@method_decorator(cache_page(60), name='dispatch')
class BookListView(ListView):
    model = Book
    template_name = 'library/book_list.html'
    context_object_name = 'books'
    paginate_by = 10
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genre_stats'] = get_books_by_genre_count()
        context['total_books'] = Book.objects.count()
        return context