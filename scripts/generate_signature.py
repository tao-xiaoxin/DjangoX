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
APP_SECRET = settings.REQUEST_APP_SECRET
BASE_URL = settings.DOMAIN_HOST


def encrypt_with_aes(data, key):
    iv = os.urandom(16)
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data.encode()) + padder.finalize()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ct = encryptor.update(padded_data) + encryptor.finalize()
    return base64.b64encode(iv + ct).decode('utf-8')


def calculate_signature(string_to_sign):
    return hmac.new(APP_SECRET.encode('utf-8'), string_to_sign.encode(), hashlib.sha256).hexdigest()


def generate_headers(method, path):
    timestamp = str(int(time.time() * 1000))
    nonce = uuid.uuid4().hex
    sign_key = uuid.uuid4().hex.encode()  # 32 bytes

    string_to_sign = f"RefererAuth REQUEST-AUTO-SA||{APP_KEY}||{timestamp}||{nonce}||{method}||{path}"
    signature = calculate_signature(string_to_sign)

    auth_string = f"RefererAuth REQUEST-AUTO-SA||{APP_KEY}||{timestamp}||{nonce}||{method}||{path}||{base64.b64encode(signature.encode()).decode()}"
    encrypted_auth = encrypt_with_aes(auth_string, sign_key)

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
    method = input("Enter HTTP method (e.g., GET, POST,PUT): ").strip().upper()
    path = input("Enter request path (e.g., /api/example): ").strip()
    debug_request(method, path)
