# -*- coding: utf-8 -*-

"""
@Remark: 接口安全（接口数据校验）
"""
import base64
import hashlib
import hmac
import logging
import time
from functools import wraps

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse

"""
使用方法，一般使用@mtg_sig，如果是drf中需要
from django.utils.decorators import method_decorator
mtg_sig = RequestSecurity()
然后再具体的请求方法前面如get、post前面添加：@method_decorator(mtg_sig)
客户端需要在http头部添加头部添加对应字段 
"""


class RequestSecurity:
    """
    用于验证Request-Sig签名的类。
    可以作为装饰器或中间件使用。
    X-Request-Auth 加密规则:
        1.生成待签名字符串,格式:请求头 REQUEST-AUTO-SA||APP_KEY||时间戳||随机数||请求方法||请求路径||计算签名结果(使用Base64编码)
        2.使用AES加密数据 (AES/CBC/PKCS5Padding)
        3.使用Base64编码
    """

    def __init__(self, app_key=settings.REQUEST_APP_KEY, app_secret=settings.REQUEST_APP_SECRET,
                 sign_expiration=settings.REQUEST_EXPIRATION):
        self.app_key = app_key
        self.app_secret = app_secret
        self.sign_expiration = sign_expiration

    def decrypt_with_aes(self, encrypted_data, bytes_key):
        """
        使用AES解密数据
        :param encrypted_data: 要解密的数据（Base64编码的字符串）
        :param bytes_key: AES密钥 256 字节
        :return: 解密后的字符串
        """
        bytes_key = bytes(bytes_key, encoding="utf8")
        encrypted_data = base64.b64decode(encrypted_data)
        iv, encrypted_data = encrypted_data[:16], encrypted_data[16:]
        cipher = Cipher(algorithms.AES(bytes_key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
        return self._unpad(decrypted_data).decode()

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s) - 1:])]

    def decrypt_device_fingerprint(self, encrypted_fingerprint, sign_key):
        decoded_data = base64.b64decode(encrypted_fingerprint)
        return self.decrypt_with_aes(decoded_data, sign_key)

    def _build_string_to_sign(self, timestamp, nonce, request_path):
        """
        构建待签名字符串的方法。
        :param timestamp: 时间戳
        :param nonce: 随机数
        :param request_path: 请求路径
        :return: 待签名字符串
        """
        return f"RefererAuth REQUEST-AUTO-SA||{self.app_key}||{timestamp}||{nonce}||{request_path}"

    def calculate_signature(self, string_to_sign):
        """
        计算签名的方法。
        使用 HMAC-SHA256 算法生成签名。
        """
        return hmac.new(self.app_secret.encode('utf-8'), msg=string_to_sign.encode(),
                        digestmod=hashlib.sha256).hexdigest()

    @staticmethod
    def parse_auth_header(auth_header):
        """
        解析授权头并返回一个字典，包含解析后的各个部分。
        :param auth_header: 授权头字符串
        :return: 解析后的字典
        """
        try:
            auth_parts = auth_header.split(' ', 1)
            client_referer_list = auth_parts[1].split('||', 6)
            return {
                "referer_auth": auth_parts[0],
                "keyword": client_referer_list[0].strip(),
                'credential': client_referer_list[1].strip(),
                'time_stamp': client_referer_list[2].strip(),
                'sign_key': client_referer_list[3].strip(),
                'method': client_referer_list[4].strip(),
                'req_path': client_referer_list[5].strip(),
                'signature_header': base64.b64decode(client_referer_list[6].strip()).decode()
            }
        except Exception as e:
            logging.error(f"Failed to parse auth header: {str(e)}")
            return None

    def verify(self, request):
        """
        验证请求的方法。
        :param request: Django HttpRequest对象
        :return: 验证结果和通用错误消息
        """
        try:
            # 步骤1：验证必要的请求头是否存在
            headers = request.headers
            required_headers = ['Referer', 'X-Request-Auth', 'X-Request-Date', 'X-Request-Sign']
            if not all(header in headers for header in required_headers):
                return False, "Request validation failed"

            # 提取必要的请求头信息
            req_url = headers['Referer']
            signature_base64 = headers['X-Request-Auth']
            req_time = headers['X-Request-Date']
            sign_key = headers['X-Request-Sign']  # 推荐使用UUID3

            # 步骤2：验证请求URL是否在允许的白名单中
            if not any(req_url.startswith(pattern) for pattern in settings.CORS_ORIGIN_WHITELIST):
                return False, "Request validation failed"

            # 步骤3：验证请求时间戳是否在允许范围内（5分钟内）
            current_time = int(time.time() * 1000)
            if abs(int(req_time) - current_time) > 300000:  # 5 minutes
                return False, "Request validation failed"

            # 步骤4：验证签名密钥长度
            sign_key = base64.b64decode(sign_key)
            if len(sign_key) != 32:
                return False, "Request validation failed"

            # 步骤5：解密并解析认证头
            auth_header = self.decrypt_device_fingerprint(signature_base64, sign_key)
            auth_data = self.parse_auth_header(auth_header)
            if not auth_data:
                return False, "Request validation failed"

            # 步骤6：验证认证头中的各个字段
            validations = {
                'referer_auth': 'RefererAuth',
                'credential': self.app_key,
                'keyword': 'REQUEST-AUTO-SA',
                'method': request.method,
                'req_path': request.path,
                'time_stamp': req_time
            }
            if not all(auth_data.get(key) == value for key, value in validations.items()):
                return False, "Request validation failed"

            # 步骤7：验证签名
            string_to_sign = self._build_string_to_sign(req_time, sign_key.hex(), request.method)
            calculated_signature = self.calculate_signature(string_to_sign)
            if not hmac.compare_digest(auth_data['signature_header'], calculated_signature):
                return False, "Request validation failed"

            # 步骤8：防止重放攻击
            nonce_key = f"authapi_{sign_key.hex()}"
            if cache.get(nonce_key):
                return False, "Request validation failed"

            # 步骤9：所有验证通过，将nonce存入缓存
            cache.set(nonce_key, "1", self.sign_expiration)
            return True, None

        except Exception as e:
            logging.error(f"Verification failed: {str(e)}")
            return False, "Request validation failed"

    def __call__(self, view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            is_valid, message = self.verify(request)
            if not is_valid:
                return JsonResponse({"code": 4003, "msg": message, "data": None}, status=200)
            return view_func(request, *args, **kwargs)

        return wrapped_view
