from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import render
from .models import Book
from .serializers import BookSerializer

# === Кастомный Permission для проверки прав на объект ===
class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Чтение разрешено всем авторизованным
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        # Изменение/удаление только владельцу
        return obj.owner == request.user

# === API Views ===
class BookListCreateView(ListCreateAPIView):
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Показываем только книги владельца
        return Book.objects.filter(owner=user)

    def perform_create(self, serializer):
        instance = serializer.save(owner=self.request.user)
        # В простой реализации право view_book автоматически у владельца
        # (аналог assign_perm из django-guardian)

class BookDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

# === Template Views ===
def login_view(request):
    return render(request, 'books/login.html')

def books_view(request):
    return render(request, 'books/book_list.html')

# === Auth Check ===
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_auth(request):
    return Response({
        'authenticated': True,
        'user_id': request.user.id,
        'username': request.user.username
    })