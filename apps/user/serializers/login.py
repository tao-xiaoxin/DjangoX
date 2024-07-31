import re

from django.db.models import Q

from ..models import Users
from datetime import datetime, timedelta
from captcha.views import CaptchaStore
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from utils.validator import CustomValidationError
# from utils.request_util import save_login_log
# from django_redis import get_redis_connection
from django.conf import settings
from configs.config import IS_SINGLE_TOKEN


class LoginSerializer(TokenObtainPairSerializer):
    """
    登录的序列化器:
    重写djangorestframework-simplejwt的序列化器
    """
    account_name = serializers.CharField(max_length=100, help_text="用户账号",
                                         error_messages={
                                             "blank": "用户账号不可以为空!",
                                             "invalid": "用户账号必须是字符类型!",
                                             "max_length": "用户账号长度不能超过100个字符!"
                                         }
                                         )
    verify_key = serializers.CharField(max_length=200, help_text="图片验证码key",
                                       error_messages={
                                           "max_length": "图片验证码key长度不能超过200个字符!"
                                       }
                                       )
    verify_value = serializers.CharField(max_length=6, help_text="图片验证码",
                                         error_messages={
                                             "max_length": "图片验证码长度不能超过6个字符!"
                                         }
                                         )
    password = serializers.CharField(max_length=50, help_text="密码",
                                     error_messages={
                                         "blank": "密码不可以为空!",
                                         "max_length": "密码长度不能超过50个字符!"
                                     }
                                     )

    class Meta:
        model = Users
        fields = ['account_name', 'verify_key', 'verify_value', 'password']

    default_error_messages = {
        'no_active_account': _('该账号已被禁用,请联系管理员')
    }

    # 开启验证码验证
    def validate_captcha(self):
        """
        验证图片验证码
        """
        try:
            # 从数据库中获取验证码对象
            o_captcha = CaptchaStore.objects.get(hashkey=self.initial_data['verify_key'])
            # 计算时间差
            seconds_ago = datetime.now() - timedelta(seconds=settings.CAPTCHA_EXPIRE_TIME)
            # 检查验证码是否过期
            if o_captcha.expiration < seconds_ago:
                o_captcha.delete()
                raise CustomValidationError("验证码已过期！")
            else:
                # 验证用户输入的验证码是否正确
                if str(o_captcha.response) == str(self.initial_data['verify_value']):
                    o_captcha.delete()
                else:
                    o_captcha.delete()
                    raise CustomValidationError("验证码输入有误！")
        except CaptchaStore.DoesNotExist:
            raise CustomValidationError("图片验证码错误！")  # 验证码不正确时抛出错误

    def validate(self, attrs):
        # 验证图片验证码
        # self.validate_captcha()
        # account_name可能是邮箱，手机号，用户名
        account_name = attrs.get('account_name')
        password = attrs.get('password')
        # 使用 Q 对象进行查询
        user = Users.objects.filter(
            Q(mobile=account_name) | Q(email=account_name) | Q(username=account_name)
        ).first()

        if not user:
            result = {
                "code": 4000,
                "msg": "账号/密码不正确",
                "data": None
            }
            return result

        if user and not user.is_active:
            result = {
                "code": 4000,
                "msg": "该账号已被禁用,请联系管理员",
                "data": None
            }
            return result

        if user and user.check_password(password):  # check_password() 对明文进行加密,并验证
            data = super().validate(attrs)
            refresh = self.get_token(self.user)

            data['name'] = self.user.name
            data['userId'] = self.user.user_id
            data['refresh'] = str(refresh)
            data['access'] = str(refresh.access_token)
            request = self.context.get('request')
            request.user = self.user
            # 记录登录成功日志
            # save_login_log(request=request)
            # 缓存用户的jwt token
            # if IS_SINGLE_TOKEN:
            #     redis_conn = get_redis_connection("singletoken")
            #     k = "lybbn-single-token{}".format(user.id)
            #     TOKEN_EXPIRE_CONFIG = getattr(settings, 'SIMPLE_JWT', None)
            #     if TOKEN_EXPIRE_CONFIG:
            #         TOKEN_EXPIRE = TOKEN_EXPIRE_CONFIG['ACCESS_TOKEN_LIFETIME']
            #         redis_conn.set(k, data['access'], TOKEN_EXPIRE)
            result = {
                "code": 200,
                "msg": "请求成功",
                "data": data
            }
        else:
            result = {
                "code": 400,
                "msg": "账号/密码不正确",
                "data": None
            }
        return result
