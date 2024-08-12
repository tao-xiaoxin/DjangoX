from unittest import TestCase

from captcha.models import CaptchaStore
from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory
from django.urls import reverse
from user.views.signup import SignUpView


class TestSignUpView(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = SignUpView.as_view()
        self.url = reverse('signup')

    def test_post(self):
        for i in range(10):
            hash_key = CaptchaStore.generate_key()
            verify_value = CaptchaStore.objects.get(hashkey=hash_key).response
            data = {
                'username': f'testuser{i}',
                'verify_key': hash_key,
                'verify_value': verify_value,
                'password': 'SecureP@ssw0rd!',
                'password2': 'SecureP@ssw0rd!',
                'email': f'testuser{i}@example.com',
                'mobile': f'1380013800{i}',
                'avatar': 'http://example.com/avatar.jpg',
                'nickname': f'TestUserNick{i}',
                'gender': i % 2,
            }
            response = self.client.post(self.url, data)
            print(response.data)
            self.assertEqual(response.data['msg'], '注册成功！')
