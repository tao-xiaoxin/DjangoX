"""
日志 django中间件
"""
import json, re
import logging
from django.utils.deprecation import MiddlewareMixin

from apps.system.models import OperationLog
from utils.request_util import get_request_user, get_request_ip, get_request_data, get_request_path, get_os, \
    get_browser, get_verbose_name
from typing import Optional
from django.http import HttpResponseForbidden, HttpResponse
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from django_redis import get_redis_connection
from django.contrib.auth.models import AnonymousUser
import hashlib
import time
from django.http import JsonResponse
from django.conf import settings


class ApiLoggingMiddleware(MiddlewareMixin):
    """
    用于记录API访问日志中间件
    """

    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.enable = getattr(settings, 'API_LOG_ENABLE', None) or False
        self.methods = getattr(settings, 'API_LOG_METHODS', None) or set()
        self.request_modular = ""

    @classmethod
    def __handle_request(cls, request):
        request.request_ip = get_request_ip(request)
        request.request_data = get_request_data(request)
        request.request_path = get_request_path(request)

    def __handle_response(self, request, response):
        # request_data,request_ip由PermissionInterfaceMiddleware中间件中添加的属性
        body = getattr(request, 'request_data', {})
        # 请求含有password则用*替换掉(暂时先用于所有接口的password请求参数)
        if isinstance(body, dict) and body.get('password', ''):
            body['password'] = '*' * len(body['password'])
        if isinstance(body, dict) and body.get('oldPassword', '') and body.get('newPassword', '') and body.get(
                'newPassword2', ''):
            body['oldPassword'] = '*' * len(body['oldPassword'])
            body['newPassword'] = '*' * len(body['newPassword'])
            body['newPassword2'] = '*' * len(body['newPassword2'])
        if not hasattr(response, 'data') or not isinstance(response.data, dict):
            response.data = {}
        try:
            if not response.data and response.content:
                content = json.loads(response.content.decode())
                response.data = content if isinstance(content, dict) else {}
        except Exception:
            return
        user = get_request_user(request)
        info = {
            'request_ip': getattr(request, 'request_ip', 'unknown'),
            'creator': user if not isinstance(user, AnonymousUser) else None,
            'dept_belong_id': getattr(request.user, 'dept_id', None),
            'request_method': request.method,
            'request_path': request.request_path,
            'request_body': body,
            'response_code': response.data.get('code'),
            'request_os': get_os(request),
            'request_browser': get_browser(request),
            'request_msg': request.session.get('request_msg'),
            'status': True if response.data.get('code') in [2000, ] else False,
            'json_result': {"code": response.data.get('code'), "msg": response.data.get('msg')},
        }

        if not self.request_modular and settings.API_MODEL_MAP.get(request.request_path, None):
            temp_request_modular = settings.API_MODEL_MAP[request.request_path]
        else:
            temp_request_modular = self.request_modular

        operation_log = OperationLog.objects.create(request_modular=temp_request_modular, request_ip=info['request_ip'],
                                                    creator=info['creator'], request_method=info['request_method'],
                                                    request_path=info['request_path'],
                                                    request_body=info['request_body'],
                                                    response_code=info['response_code'], request_os=info['request_os'],
                                                    request_browser=info['request_browser'],
                                                    request_msg=info['request_msg'], status=info['status'],
                                                    json_result=info['json_result'])

        self.request_modular = ""

    def process_view(self, request, view_func, view_args, view_kwargs):
        if hasattr(view_func, 'cls') and hasattr(view_func.cls, 'queryset'):
            if self.enable:
                if self.methods == 'ALL' or request.method in self.methods:
                    self.request_modular = get_verbose_name(view_func.cls.queryset)

        return None

    def process_request(self, request):
        self.__handle_request(request)

    def process_response(self, request, response):
        """
        主要请求处理完之后记录
        :param request:
        :param response:
        :return:
        """
        if self.enable:
            if self.methods == 'ALL' or request.method in self.methods:
                self.__handle_response(request, response)

        return response


class SingleTokenMiddleware(MiddlewareMixin):
    """
    保证设备登录的唯一性
    """

    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.enable = getattr(settings, 'IS_SINGLE_TOKEN', False)
        self.jwt_config = getattr(settings, 'SIMPLE_JWT', {})
        self.redis_conn = get_redis_connection("single_token")

    @staticmethod
    def _get_request_info(request):
        request.request_ip = get_request_ip(request)
        request.request_data = get_request_data(request)
        request.request_path = get_request_path(request)

    def _get_jwt_token(self, request) -> Optional[str]:
        jwt_token = request.META.get('HTTP_AUTHORIZATION')
        if not jwt_token:
            return None

        auth_type = self.jwt_config.get('AUTH_HEADER_TYPES', ('Bearer',))[0]
        if auth_type not in jwt_token:
            return None

        token = jwt_token.split(auth_type)[1].strip()
        return token if token != 'null' else None

    def _validate_token(self, request, token):
        try:
            user, _ = JWTTokenUserAuthentication().authenticate(request)
            cache_key = f"single_token_{user.user_id}"
            cached_token = self.redis_conn.get(cache_key)

            if not cached_token or str(token) != str(cached_token):
                return False
            return True
        except Exception as e:
            logging.error(f"Token validation error: {e}")
            return False

    def process_request(self, request):
        self._get_request_info(request)

        if not self.enable or not self.jwt_config:
            return None

        if request.request_path[:9] in settings.FRONTEND_API_LIST:
            return None

        token = self._get_jwt_token(request)
        if not token:
            return None

        if not self._validate_token(request, token):
            error_data = {
                'msg': '身份认证已经过期，请重新登入！',
                'code': 4001,
                'data': None
            }
            return JsonResponse(error_data, status=200, charset='utf-8')

        return None


class StandardJSONMiddleware(MiddlewareMixin):
    """
    标准化JSON响应中间件
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 正常处理请求
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        # 检查异常是否具有我们期望的属性
        if hasattr(exception, 'code') and hasattr(exception, 'error') and hasattr(exception, 'detail'):
            # 构建标准的错误响应数据
            data = {
                'code': exception.code,
                'error': exception.error,
                'detail': exception.detail
            }

            # 特殊处理 DateOutOfSync 异常
            if isinstance(exception, DateOutOfSync):
                data['server_time'] = exception.server_time

            # 根据异常类型设置适当的HTTP状态码
            status_code = 500  # 默认为500 Internal Server Error
            if isinstance(exception, HTTP404):
                status_code = 404
            elif isinstance(exception, HTTP400):
                status_code = 400
            elif isinstance(exception, HTTP401):
                status_code = 401
            elif isinstance(exception, HTTP403):
                status_code = 403

            # 返回JSON格式的响应
            return JsonResponse(data, status=status_code)

        # 如果不是我们处理的异常类型，返回None让Django继续处理
        return None


class SignatureMiddleware(MiddlewareMixin):
    """
    校验签名中间件,反爬虫
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 白名单路径,不需要签名验证
        exempt_paths = ['/api/login', '/api/register']
        if request.path in exempt_paths:
            return self.get_response(request)

        # 获取请求头中的签名信息
        signature = request.headers.get('X-Signature')
        timestamp = request.headers.get('X-Timestamp')
        app_key = request.headers.get('X-App-Key')

        if not all([signature, timestamp, app_key]):
            return JsonResponse({'error': 'Missing signature information'}, status=400)

        # 检查时间戳是否在允许的时间范围内
        current_time = int(time.time())
        if abs(current_time - int(timestamp)) > settings.SIGNATURE_EXPIRATION:
            return JsonResponse({'error': 'Signature expired'}, status=400)

        # 获取 app secret
        app_secret = settings.APP_SECRETS.get(app_key)
        if not app_secret:
            return JsonResponse({'error': 'Invalid app key'}, status=400)

        # 构造签名字符串
        signature_string = f"{app_key}{timestamp}"

        # 如果是 GET 请求,将查询参数按字母顺序排序后加入签名字符串
        if request.method == 'GET':
            params = sorted(request.GET.items())
            signature_string += ''.join(f"{k}{v}" for k, v in params)
        # 如果是 POST 请求,将 body 加入签名字符串
        elif request.method == 'POST':
            signature_string += request.body.decode()

        # 计算签名
        calculated_signature = hashlib.md5((signature_string + app_secret).encode()).hexdigest()

        # 验证签名
        if calculated_signature != signature:
            return JsonResponse({'error': 'Invalid signature'}, status=400)

        return self.get_response(request)
