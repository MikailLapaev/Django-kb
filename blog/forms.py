from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'category', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Введите заголовок поста',
                'class': 'form-input'
            }),
            'category': forms.Select(attrs={
                'class': 'form-input'
            }),
            'content': forms.Textarea(attrs={
                'placeholder': 'Напишите содержание поста...',
                'class': 'form-textarea',
                'rows': 10
            }),
        }