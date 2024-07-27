from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from apps.user.models import Users
from django_redis import get_redis_connection
from captcha.models import CaptchaStore
from datetime import datetime, timedelta
from application.settings import CAPTCHA_EXPIRE_TIME

class TestSignUpView(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('signup')  # Adjust the URL name as per your URL configuration
        self.captcha_key = 'testkey'
        self.captcha_value = '123456'
        self.captcha = CaptchaStore.objects.create(
            response=self.captcha_value,
            hashkey=self.captcha_key,
            expiration=datetime.now() + timedelta(seconds=CAPTCHA_EXPIRE_TIME)
        )

    def test_post_success(self):
        data = {
            'username': 'testuser',
            'verify_key': self.captcha_key,
            'verify_value': self.captcha_value,
            'password': 'TestPass123',
            'password2': 'TestPass123',
            'email': 'test@example.com',
            'mobile': '12345678901',
            'avatar': 'http://example.com/avatar.jpg',
            'nickname': 'Test Nickname',
            'gender': 'male'
        }
        response = self.client.post(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('msg'), '注册成功！')
        self.assertTrue(Users.objects.filter(username='testuser').exists())

    def test_post_failure(self):
        data = {
            'username': 'testuser',
            'verify_key': self.captcha_key,
            'verify_value': 'wrongvalue',
            'password': 'TestPass123',
            'password2': 'TestPass123',
            'email': 'test@example.com',
            'mobile': '12345678901',
            'avatar': 'http://example.com/avatar.jpg',
            'nickname': 'Test Nickname',
            'gender': 'male'
        }
        response = self.client.post(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('验证码错误！', response.json().get('detail'))