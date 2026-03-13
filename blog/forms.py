# blog/forms.py
from django import forms
from .models import Post, Comment, Category
from .validators import (
    sanitize_input, validate_forbidden_patterns,
    validate_post_title, validate_post_content,
    validate_category_name, validate_comment_content,
    validate_password_strength, validate_email_domain,
    validate_username_business_rule, validate_first_name_cyrillic
)
from django.contrib.auth.models import User


class PostForm(forms.ModelForm):
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'type': 'text',
            'placeholder': 'Введите заголовок поста'
        }),
        label='Заголовок'
    )
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': '10',
            'placeholder': 'Введите содержание поста (минимум 50 символов)'
        }),
        label='Содержание'
    )
    
    class Meta:
        model = Post
        fields = ['title', 'content', 'category']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'})
        }
    
    def clean_title(self):
        title = self.cleaned_data.get('title', '')
        title = sanitize_input(title)
        validate_forbidden_patterns(title, 'Заголовок')
        validate_post_title(title)
        return title
    
    def clean_content(self):
        content = self.cleaned_data.get('content', '')
        content = sanitize_input(content)
        validate_forbidden_patterns(content, 'Содержание')
        validate_post_content(content)
        return content


class CommentForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': '4',
            'placeholder': 'Введите комментарий (минимум 10 символов)'
        }),
        label='Комментарий'
    )
    
    class Meta:
        model = Comment
        fields = ['content']
    
    def clean_content(self):
        content = self.cleaned_data.get('content', '')
        content = sanitize_input(content)
        validate_forbidden_patterns(content, 'Комментарий')
        validate_comment_content(content)
        return content


class CategoryForm(forms.ModelForm):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'type': 'text',
            'placeholder': 'Название категории'
        }),
        label='Название категории'
    )
    
    class Meta:
        model = Category
        fields = ['name']
    
    def clean_name(self):
        name = self.cleaned_data.get('name', '')
        name = sanitize_input(name)
        validate_forbidden_patterns(name, 'Название категории')
        validate_category_name(name)
        return name


class RegistrationForm(forms.Form):
    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'type': 'text',
            'placeholder': 'Придумайте имя пользователя'
        }),
        label='Имя пользователя'
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'type': 'text',
            'placeholder': 'Введите email'
        }),
        label='Email'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'type': 'text',
            'placeholder': 'Придумайте пароль'
        }),
        label='Пароль'
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'type': 'text',
            'placeholder': 'Подтвердите пароль'
        }),
        label='Подтверждение пароля'
    )
    first_name = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'type': 'text',
            'placeholder': 'Ваше имя (только кириллица)'
        }),
        label='Имя'
    )
    
    def clean_username(self):
        username = self.cleaned_data.get('username', '')
        username = sanitize_input(username)
        validate_forbidden_patterns(username, 'Имя пользователя')
        validate_username_business_rule(username)
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('Пользователь с таким именем уже существует.')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email', '')
        email = sanitize_input(email)
        validate_email_domain(email)
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Email уже зарегистрирован.')
        return email
    
    def clean_password(self):
        password = self.cleaned_data.get('password', '')
        validate_password_strength(password)
        return password
    
    def clean_password_confirm(self):
        password = self.cleaned_data.get('password', '')
        password_confirm = self.cleaned_data.get('password_confirm', '')
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('Пароли не совпадают.')
        return password_confirm
    
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name', '')
        if first_name:
            first_name = sanitize_input(first_name)
            validate_first_name_cyrillic(first_name)
        return first_name
    
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username', '')
        first_name = cleaned_data.get('first_name', '')
        if 'test' in username.lower() and not first_name:
            raise forms.ValidationError('Для тестовых аккаунтов необходимо указать имя.')
        return cleaned_data


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'type': 'text',
            'placeholder': 'Имя пользователя'
        }),
        label='Имя пользователя'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'type': 'text',
            'placeholder': 'Пароль'
        }),
        label='Пароль'
    )
    
    def clean_username(self):
        username = self.cleaned_data.get('username', '')
        username = sanitize_input(username)
        if not username:
            raise forms.ValidationError('Введите имя пользователя.')
        return username
    
    def clean_password(self):
        password = self.cleaned_data.get('password', '')
        if not password:
            raise forms.ValidationError('Введите пароль.')
        return password