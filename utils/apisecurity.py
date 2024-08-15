# -*- coding: utf-8 -*-

"""
@Remark: 接口安全（接口数据校验）
"""
import logging

from utils.json_response import ErrorResponse
from .common import md5
from django_redis import get_redis_connection
import base64
import hashlib
import hmac
import time
from functools import wraps
from django.conf import settings
from django.http import JsonResponse

visited_keys = {
    # "332d3ddklllskkdwwwiissswewsw":时间
}

"""
使用方法，一般使用@mtg_sig，如果是drf中需要
from django.utils.decorators import method_decorator
mtg_sig = MTGSigServer()
然后再具体的请求方法前面如get、post前面添加：@method_decorator(mtg_sig)
客户端需要在http头部添加mtgsig头部字段 
"""


class RequestSigServer:
    """
    用于验证Request-Sig签名的类。
    可以作为装饰器或中间件使用。
    """

    def __init__(self, app_key=settings.REQUEST_APP_KEY, app_secret=settings.REQUEST_APP_KEY,
                 secret_key=settings.REQUEST_APP_SECRET, sign_expiration=settings.REQUEST_EXPIRATION):
        """
        初始化MTGSigServer实例。
        :param app_key: 应用的API密钥。
        :param app_secret: 应用的API密钥。
        :param sign_expiration: 签名有效期（秒）。
        """
        self.app_key = app_key
        self.app_secret = app_secret
        self.secret_key = secret_key
        self.sign_expiration = sign_expiration  # nonce有效期(秒)

    @staticmethod
    def _build_canonical_request(http_method, path, headers, params, body):
        """
        构建规范请求串。
        """
        canonical_headers = '\n'.join(f"{k.lower()}:{v}" for k, v in sorted(headers.items()))
        signed_headers = ';'.join(sorted(k.lower() for k in headers.keys()))
        canonical_querystring = '&'.join(f"{k}={v}" for k, v in sorted(params.items()))
        payload_hash = hashlib.sha256(body.encode('utf-8')).hexdigest() if body else hashlib.sha256(b'').hexdigest()
        return f"{http_method}\n{path}\n{canonical_querystring}\n{canonical_headers}\n{signed_headers}\n{payload_hash}"

    @staticmethod
    def _build_string_to_sign(timestamp, nonce, canonical_request):
        """
        构建待签名字符串。
        """
        return f"MTG-HMAC-SA\n{timestamp}\n{nonce}\n{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"

    def calculate_signature(self, string_to_sign):
        """
        计算签名。
        """
        key = hmac.new(self.app_secret.encode('utf-8'), self.app_key.encode('utf-8'), hashlib.sha256).digest()
        return base64.b64encode(hmac.new(key, string_to_sign.encode('utf-8'), hashlib.sha256).digest()).decode('utf-8')

    def verify(self, request):
        """

        try:
            auth_header = request.META.get('HTTP_AUTH_API')
            if not auth_header:
                return ErrorResponse(msg='缺少认证头部信息')
            client_md5, client_time, random_str = auth_header.split('|', maxsplit=2)
        except Exception as e:
            return ErrorResponse(msg="接口安全校验值错误")
        client_float_time = float(client_time)

        if len(random_str) != 5:
            return ErrorResponse(msg="第五个字段只能为5位")


        if (client_float_time + 200) < server_float_time:
            return ErrorResponse(msg='接口校验时间过期')


        server_md5 = md5("%s|%s|%s" % (settings.REQUEST_SECRET_KEY, client_time, random_str))
        if server_md5 != client_md5:
            return ErrorResponse(msg='接口加密校验失败')


        client = get_redis_connection('authapi')
        if client.get(client_md5):
            return ErrorResponse(msg='该校验头部您已经使用过，请使用新的校验信息')

        """

        try:
            # 获取认证头
            auth_header = request.headers.get('X-Request-Auth')
            # 从请求头中获取时间戳和sign
            timestamp = request.headers.get('X-Request-Date')
            sign = request.headers.get('X-Request-Sign')
            if not auth_header or not timestamp or not sign:
                return False, "Missing Authorization header!"

            # 解析认证头
            auth_parts = auth_header.split(',')
            credential = auth_parts[0].split(' ')[1].split('=')[1]
            signature_base64 = auth_parts[1].split('=')[1].strip()

            # 从Base64解码签名
            try:
                signature = base64.b64decode(signature_base64)
            except:
                return False, "Invalid signature encoding"
            cache = get_redis_connection('authapi')

            # 第一重验证（时间戳校验）,检查时间戳是否在允许的范围内
            server_float_time = time.time()
            current_time = int(time.time() * 1000)
            if abs(int(timestamp) - current_time) > 300000:  # 允许5分钟的时间差
                return False, "Timestamp out of range"
            # 第二重验证（md5校验）
            body = request.body.decode('utf-8') if request.body else ''
            canonical_request = self._build_canonical_request(request.method, request.path, request.headers,
                                                              request.GET, body)
            string_to_sign = self._build_string_to_sign(timestamp, sign, canonical_request)
            calculated_signature = self.calculate_signature(string_to_sign)
            # 验证签名
            if credential != self.app_key:
                return False, "Invalid credential"

            # 比较签名
            if calculated_signature != signature_base64:
                return False, "Invalid signature"
            # 第三重验证（第几次访问校验）采用redis验证(增加md5+ip方式存储解决不同ip下的并发访问问题)
            nonce_key = f"mtgsig:nonce:{sign}"
            if cache.get(nonce_key):
                return False, "Nonce already used"
            # 如果所有检查都通过，将nonce添加到Redis缓存中
            cache.set(nonce_key, "1", self.nonce_expiration)
            # cache.set(client_md5, client_float_time, ex=86400)  # 1天有效期
            return True, "Verification successful"
        except Exception as e:
            logging.error(f"Verification failed: {str(e)}")
            return False, f"Verification failed: {str(e)}"

    def __call__(self, view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            is_valid, message = self.verify(request)
            if not is_valid:
                data = {"code": 4003, "msg": message, "data": None}
                return JsonResponse(data, status=200)
            return view_func(request, *args, **kwargs)

        return wrapped_view
