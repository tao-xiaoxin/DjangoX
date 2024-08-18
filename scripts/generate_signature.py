# -*- coding: utf-8 -*-

"""
@Remark: 生成签名
"""
import base64
import hashlib
import hmac
import time
import uuid
import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from django.conf import settings

# 配置信息
APP_KEY = settings.REQUEST_APP_KEY
BASE_URL = settings.DOMAIN_HOST


class SignatureGenerator:
    def __init__(self, sign_key, app_secret=settings.REQUEST_APP_SECRET):
        """
        初始化签名生成器
        :param sign_key: AES密钥 动态生成
        :param app_secret: APP_SECRET 默认为配置文件中的REQUEST_APP_SECRET
        """
        self.aes_key = sign_key
        self.app_secret = app_secret

    def encrypt_with_aes(self, data, key):
        """
        使用AES加密数据
        :param data: 要加密的数据
        :param key: AES密钥 256 字节
        :return:
        """
        if len(key) != 32:  # 256位密钥应该是32字节
            raise ValueError("Invalid key size for AES")
        iv = os.urandom(16)  # 生���随机的初始化向量
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        padded_data = self._pad(data.encode())
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        return base64.b64encode(iv + encrypted_data).decode()  # 将IV和加密数据一起返回

    def _pad(self, s):
        """
        填充数据以确保其长度是16字节的倍数
        :param s:
        :return:
        """
        return s + (16 - len(s) % 16) * chr(16 - len(s) % 16).encode()

    def calculate_signature(self, string_to_sign):
        """
        计算签名
        """
        hash_sign = hmac.new(self.app_secret.encode('utf-8'), msg=string_to_sign.encode(),
                             digestmod=hashlib.sha256).hexdigest()
        print(f"Hash Sign: {hash_sign}")
        return base64.b64encode(hash_sign.encode()).decode()

    def generate_signature(self, data):
        encrypted_data = self.encrypt_with_aes(data, self.aes_key)

        print(f"Encrypted Data: {encrypted_data}")
        return encrypted_data


def generate_headers(method, path):
    timestamp = str(int(time.time() * 1000))
    nonce = uuid.uuid4().hex
    sign_key = nonce.encode()  # 32 bytes
    g = SignatureGenerator(sign_key)
    string_to_sign = f"RefererAuth REQUEST-AUTO-SA||{APP_KEY}||{timestamp}||{nonce}||{method}||{path}"
    print(f"String to Sign: {string_to_sign}")
    base64_signature = g.calculate_signature(string_to_sign)
    print(f"Base64 Signature: {base64_signature}")
    auth_string = f"RefererAuth REQUEST-AUTO-SA||{APP_KEY}||{timestamp}||{nonce}||{method}||{path}||{base64_signature}"
    print(f"Auth String: {auth_string}")
    encrypted_auth = g.generate_signature(data=auth_string)

    headers = {
        'Referer': BASE_URL,
        'X-Request-Auth': encrypted_auth,
        'X-Request-Date': timestamp,
        'X-Request-Sign': base64.b64encode(sign_key).decode(),
    }

    return headers


def debug_request(method, path):
    full_url = BASE_URL + path
    headers = generate_headers(method, path)

    print(f"Request URL: {full_url}")
    print("Headers:")
    for key, value in headers.items():
        print(f"  {key}: {value}")

    print("\nYou can now use these headers in your Django test client or in tools like curl or Postman.")


# 使用示例
def run():
    method = input("Enter HTTP method (e.g., GET, POST,PUT)>>> ").strip().upper()
    path = input("Enter request path (e.g., /api/example)>>>").strip()
    debug_request(method, path)
