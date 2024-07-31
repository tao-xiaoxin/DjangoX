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
        hash_key = CaptchaStore.generate_key()
        print(hash_key)
        verify_value = CaptchaStore.objects.get(hashkey=hash_key).response
        # 准备测试数据
        data = {
            'username': 'testuser',
            'verify_key': hash_key,
            'verify_value': verify_value,
            'password': 'SecureP@ssw0rd!',
            'password2': 'SecureP@ssw0rd!',
            'email': 'testuser@example.com',
            'mobile': '13800138000',
            'avatar': 'http://example.com/avatar.jpg',
            'nickname': 'TestUserNick',
            'gender': 1,
        }

        # 发送 POST 请求
        response = self.client.post(self.url, data)
        print("response", response)

        # 验证响应是否正确
        # self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['msg'], '注册成功！')
