from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import Post, Category


class UserRegistrationValidationTests(APITestCase):
    def setUp(self):
        self.url = reverse('register')

    def test_weak_password_rejected(self):
        response = self.client.post(self.url, {
            'username': 'stronguser',
            'email': 'user@gmail.com',
            'password': '123456',
            'password_confirm': '123456',
            'first_name': 'Иван',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Пароль должен содержать минимум 10 символов.', status_code=200)

    def test_password_mismatch_rejected(self):
        response = self.client.post(self.url, {
            'username': 'stronguser2',
            'email': 'user2@gmail.com',
            'password': 'StrongPass!23',
            'password_confirm': 'StrongPass!21',
            'first_name': 'Иван',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Пароли не совпадают.', status_code=200)

    def test_invalid_email_domain_rejected(self):
        response = self.client.post(self.url, {
            'username': 'stronguser3',
            'email': 'user@invalid-domain.com',
            'password': 'StrongPass!23',
            'password_confirm': 'StrongPass!23',
            'first_name': 'Иван',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Регистрация возможна только с разрешённых доменов', status_code=200)


class PostApiValidationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='apiuser',
            email='apiuser@gmail.com',
            password='StrongPass!23',
            first_name='Иван',
        )
        self.category = Category.objects.create(name='Тестовая категория')
        self.list_url = reverse('post-list')

    def test_create_post_requires_authentication(self):
        response = self.client.post(self.list_url, {
            'title': 'Новый пост',
            'content': 'Содержимое нового поста, достаточно длинное для валидации.',
            'category': self.category.id,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_post_with_invalid_title_rejected(self):
        self.client.login(username='apiuser', password='StrongPass!23')
        response = self.client.post(self.list_url, {
            'title': 'Hi',
            'content': 'Содержимое нового поста, достаточно длинное для валидации.',
            'category': self.category.id,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)

    def test_create_post_with_invalid_content_rejected(self):
        self.client.login(username='apiuser', password='StrongPass!23')
        response = self.client.post(self.list_url, {
            'title': 'Заголовок поста',
            'content': 'Коротко',
            'category': self.category.id,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('content', response.data)

    def test_create_post_success(self):
        self.client.login(username='apiuser', password='StrongPass!23')
        response = self.client.post(self.list_url, {
            'title': 'Корректный заголовок поста',
            'content': 'Содержимое нового поста, достаточно длинное и осмысленное для прохождения всех проверок.',
            'category': self.category.id,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)
