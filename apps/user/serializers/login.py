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
from django.conf import settings


class LoginSerializer(TokenObtainPairSerializer):
    """
    登录的序列化器:
    重写djangorestframework-simplejwt的序列化器
    """
    username = serializers.CharField(max_length=100, help_text="用户账号",
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
        fields = "__all__"
        read_only_fields = ["user_id"]

    default_error_messages = {
        'no_active_account': _('该账号已被禁用,请联系管理员')
    }

    @classmethod
    def get_token(cls, user):
        """
        为指定用户生成JWT令牌并添加自定义声明。

        这个方法重写了父类的 get_token 方法，允许我们向令牌中添加自定义信息。

        参数:
        user (User): 要为其生成令牌的用户对象。

        返回:
        Token: 包含自定义声明的JWT令牌对象。

        注意:
        - 添加到令牌中的信息可以被解码，因此不应包含敏感数据。
        - 这里添加的自定义声明可以在客户端使用，无需额外的服务器请求。
        """
        # 调用父类方法生成基础令牌
        token = super().get_token(user)

        # 向令牌添加自定义声明
        # 这里我们添加了用户名，可以根据需要添加其他非敏感信息
        token['name'] = user.username

        # 返回增强后的令牌
        return token

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
        # username可能是邮箱，手机号，用户名
        username = attrs.get('username')
        password = attrs.get('password')
        # 使用 Q 对象进行查询
        user = Users.objects.filter(
            Q(mobile=account_name) | Q(email=account_name) | Q(username=account_name)
        ).first()

        if not user:
            result = {
                "code": 4000,
                "msg": "账号/密码不正确！",
                "data": None
            }
            return result

        if user and not user.is_active:
            result = {
                "code": 4000,
                "msg": "该账号已被禁用,请联系管理员！",
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
            result = {
                "code": 200,
                "msg": "请求成功！",
                "data": data
            }
        else:
            result = {
                "code": 400,
                "msg": "账号/密码不正确！",
                "data": None
            }
        return result
