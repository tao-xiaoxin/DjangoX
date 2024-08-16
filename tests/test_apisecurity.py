# -*- coding: utf-8 -*-

"""
@Remark: 接口安全（接口数据校验）单元测试
"""
import unittest
from django.test import TestCase
from django.conf import settings
from django.core.cache import cache
from unittest.mock import patch, MagicMock
import base64
import time
import uuid
import hashlib
import hmac
from scripts.generate_signature import encrypt_with_aes, calculate_signature
from utils.apisecurity import RequestSecurity


class RequestSecurityTestCase(TestCase):
    def setUp(self):
        self.security = RequestSecurity()
        self.app_key = settings.REQUEST_APP_KEY
        self.app_secret = settings.REQUEST_APP_SECRET

    def test_decrypt_with_aes(self):
        encrypted_data = base64.b64encode(b'some_encrypted_data')
        key = b'0' * 32  # 32字节的key
        with patch('utils.apisecurity.Cipher') as mock_cipher:
            mock_decryptor = MagicMock()
            mock_decryptor.update.return_value = b'decrypted'
            mock_decryptor.finalize.return_value = b''
            mock_cipher.return_value.decryptor.return_value = mock_decryptor

            decrypted_data = self.security.decrypt_with_aes(encrypted_data, key)
            self.assertEqual(decrypted_data, 'decrypted')

    def test_build_string_to_sign(self):
        timestamp = "1629123456789"
        nonce = "random_nonce"
        request_path = "/api/test"
        expected_string = f"RefererAuth REQUEST-AUTO-SA||{self.app_key}||{timestamp}||{nonce}||{request_path}"
        result = self.security._build_string_to_sign(timestamp, nonce, request_path)
        self.assertEqual(result, expected_string)

    def test_calculate_signature(self):
        string_to_sign = "test_string"
        expected_signature = hmac.new(
            self.app_secret.encode('utf-8'),
            msg=string_to_sign.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()
        signature = self.security.calculate_signature(string_to_sign)
        self.assertEqual(signature, expected_signature)

    def test_parse_auth_header(self):
        auth_header = f"RefererAuth REQUEST-AUTO-SA||{self.app_key}||1629123456789||nonce||GET||/api/test||{base64.b64encode(b'signature').decode()}"
        result = self.security.parse_auth_header(auth_header)
        self.assertIsNotNone(result)
        self.assertEqual(result['credential'], self.app_key)
        self.assertEqual(result['method'], 'GET')
        self.assertEqual(result['req_path'], '/api/test')

    def test_parse_auth_header_invalid(self):
        auth_header = "InvalidHeader"
        result = self.security.parse_auth_header(auth_header)
        self.assertIsNone(result)

    @patch('utils.apisecurity.cache')
    def test_verify(self, mock_cache):
        mock_cache.get.return_value = None
        mock_request = MagicMock()
        timestamp = str(int(time.time() * 1000))
        sign_key = uuid.uuid4().hex
        method = 'GET'
        path = '/api/test'
        string_to_sign = f"RefererAuth REQUEST-AUTO-SA||{self.app_key}||{timestamp}||{sign_key}||{method}||{path}"
        signature = self.security.calculate_signature(string_to_sign)
        #
        auth_string = string_to_sign + f"||{base64.b64encode(signature.encode('utf-8')).decode('utf-8')}"+"||"
        print("加密数据:",auth_string)
        b_sign_key = sign_key.encode('utf-8')
        encrypted_auth = encrypt_with_aes(auth_string, b_sign_key)
        print("base64加密数据:",encrypted_auth)
        decoded_auth = base64.b64decode(encrypted_auth).decode('utf-8')
        print("解密数据:",decoded_auth)
        # headers = {
        #     'Referer': BASE_URL,
        #     'X-Request-Auth': encrypted_auth,
        #     'X-Request-Date': timestamp,
        #     'X-Request-Sign': base64.b64encode(sign_key.encode("utf-8")).decode(),
        # }
        # mock_request.headers = headers
        # mock_request.method = 'GET'
        # mock_request.path = '/api/test'
        #
        # with patch.object(self.security, 'decrypt_device_fingerprint', return_value="RefererAuth REQUEST-AUTO-SA||..."):
        #     with patch.object(self.security, 'parse_auth_header', return_value={
        #         'referer_auth': 'RefererAuth',
        #         'credential': self.app_key,
        #         'keyword': 'REQUEST-AUTO-SA',
        #         'method': 'GET',
        #         'req_path': '/api/test',
        #         'time_stamp': mock_request.headers['X-Request-Date'],
        #         'signature_header': 'valid_signature'
        #     }):
        #         with patch.object(self.security, 'calculate_signature', return_value='valid_signature'):
        #             with patch('utils.apisecurity.settings.CORS_ORIGIN_WHITELIST', ['https://example.com']):
        #                 is_valid, message = self.security.verify(mock_request)
        #                 self.assertTrue(is_valid)
        #                 self.assertIsNone(message)

    def test_verify_invalid_headers(self):
        mock_request = MagicMock()
        mock_request.headers = {}  # 缺少必要的头部
        is_valid, message = self.security.verify(mock_request)
        self.assertFalse(is_valid)
        self.assertEqual(message, "Request validation failed")

    # 额外的测试用例
    def test_decrypt_device_fingerprint(self):
        encrypted_fingerprint = base64.b64encode(b'encrypted_data')
        sign_key = b'0' * 32
        with patch.object(self.security, 'decrypt_with_aes', return_value='decrypted_fingerprint'):
            result = self.security.decrypt_device_fingerprint(encrypted_fingerprint, sign_key)
            self.assertEqual(result, 'decrypted_fingerprint')

    @patch('utils.apisecurity.cache')
    def test_verify_replay_attack(self, mock_cache):
        mock_cache.get.return_value = "1"  # 模拟nonce已存在
        mock_request = MagicMock()
        mock_request.headers = {
            'Referer': 'https://example.com',
            'X-Request-Auth': base64.b64encode(b'encrypted_auth_header').decode(),
            'X-Request-Date': str(int(time.time() * 1000)),
            'X-Request-Sign': base64.b64encode(uuid.uuid4().bytes).decode(),
        }
        is_valid, message = self.security.verify(mock_request)
        self.assertFalse(is_valid)
        self.assertEqual(message, "Request validation failed")


if __name__ == '__main__':
    unittest.main()
