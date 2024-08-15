# -*- coding: utf-8 -*-

"""
@Remark: 接口安全（接口数据校验）
"""
import logging
import fnmatch
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
from .request_util import get_request_data

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

    def __init__(self, app_key=settings.REQUEST_APP_KEY, app_secret=settings.REQUEST_APP_SECRET):
        """
        初始化MTGSigServer实例。
        :param app_key: 应用的API密钥。
        :param app_secret: 应用的API密钥。
        :param sign_expiration: 签名有效期（秒）。
        """
        self.app_key = app_key
        self.app_secret = app_secret
        self.sign_expiration = sign_expiration  # nonce有效期(秒)

    @staticmethod
    def _build_string_to_sign(timestamp, nonce, canonical_request):
        """
        构建待签名字符串。
        """
        return f"REQUEST-HMAC-SA-{timestamp}-{nonce}-{canonical_request}"

    def calculate_signature(self, string_to_sign):
        """
        计算签名。
        """
        # 第一步：使用 HMAC-SHA256 算法计算二进制摘要
        signature = hmac.new(self.app_secret, string_to_sign.encode('utf-8'), hashlib.sha256).digest()

        # 第二步：将二进制摘要编码为 Base64 字符串，并解码为 UTF-8 字符串
        return base64.b64encode(signature).decode('utf-8')

    def verify(self, request):
        """
        """
        request.request_data = get_request_data(request)
        print(request.request_data)
        try:
            req_url = request.headers.get('Referer')
            # 获取认证头
            signature_base64 = request.headers.get('X-Request-Auth')
            # 从请求头中获取时间戳和sign
            timestamp = request.headers.get('X-Request-Date')
            req_sign = request.headers.get('X-Request-Sign')
            if not signature_base64 or not timestamp or not req_sign or not req_url:
                return False, "Missing Authorization header！"
            # 第一重验证（请求地址校验）检查是否在CORS跨域白名单中
            if not any(fnmatch.fnmatch(req_url, pattern) for pattern in settings.CORS_ORIGIN_WHITELIST):
                return False, "Bad request URL！"
            # 第二重验证（时间戳校验）,检查时间戳是否在允许的范围内
            # current_time = int(time.time() * 1000)
            # if abs(int(timestamp) - current_time) > 300000:  # 允许5分钟的时间差
            #     return False, "Invalid Authorization！"
            # 从Base64解码签名
            try:
                signature = base64.b64decode(signature_base64)
            except:
                return False, "Invalid signature format！"
            # 请求头 APP_KEY|时间戳|请求方法|请求路径|
            # 解析认证头
            # auth_parts = auth_header.split('AUTO')
            # credential = auth_parts[0].split(' ')[1].split('=')[1]
            # signature_base64 = auth_parts[1].split('=')[1].strip()

            cache = get_redis_connection('authapi')

            print(canonical_request)
            # 获取请求方式
            string_to_sign = self._build_string_to_sign(timestamp, req_sign, request.method)
            calculated_signature = self.calculate_signature(string_to_sign)
            # 验证签名
            if credential != self.app_key:
                return False, "Invalid credential！"

            # 比较签名
            if calculated_signature != signature_base64:
                return False, "Invalid signature！"
            # 第三重验证（第几次访问校验）采用redis验证(增加md5+ip方式存储解决不同ip下的并发访问问题)
            nonce_key = f"authapi_{req_sign}"
            if cache.get(nonce_key):
                return False, "Invalid Signature (Replay Attack Detected)!"
            # 如果所有检查都通过，将sign添加到Redis缓存中
            cache.set(nonce_key, "1", self.nonce_expiration)
            return True, _

        except Exception as e:
            logging.error(f"Verification failed: {str(e)}")
            return False, "Network error, please try again later！"


def __call__(self, view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        is_valid, message = self.verify(request)
        if not is_valid:
            data = {"code": 4003, "msg": message, "data": None}
            return JsonResponse(data, status=200)
        return view_func(request, *args, **kwargs)

    return wrapped_view
