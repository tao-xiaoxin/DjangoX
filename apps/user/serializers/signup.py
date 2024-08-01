from datetime import datetime, timedelta
from application.settings import CAPTCHA_EXPIRE_TIME
from captcha.models import CaptchaStore
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
import logging
from utils.validator import CustomValidationError
from ..models import Users, GENDER_CHOICES
from utils.common import REGEX_MOBILE
import re
from rest_framework_simplejwt.tokens import RefreshToken


class SignUpSerializer(serializers.ModelSerializer):
    """
    注册序列化器
    """
    username = serializers.CharField(max_length=50, help_text="用户账号",
                                     error_messages={
                                         "blank": "用户账号不可以为空!",
                                         "invalid": "用户账号必须是字符类型!",
                                         "max_length": "用户账号长度不能超过50个字符!"
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
    password2 = serializers.CharField(max_length=50, help_text="确认密码",
                                      error_messages={
                                          "blank": "确认密码不可以为空!",
                                          "max_length": "确认密码长度不能超过50个字符!"
                                      }
                                      )

    email = serializers.EmailField(max_length=60, help_text="邮箱", required=False, allow_blank=True, allow_null=True,
                                   error_messages={
                                       "invalid": "请输入有效的邮箱地址!",
                                       "max_length": "邮箱长度不能超过60个字符!"
                                   }
                                   )

    mobile = serializers.CharField(max_length=11, help_text="电话", required=False, allow_blank=True, allow_null=True,
                                   error_messages={
                                       "max_length": "电话号码长度不能超过11个字符!"
                                   }
                                   )

    avatar = serializers.CharField(max_length=200, help_text="头像", required=False, allow_blank=True, allow_null=True,
                                   error_messages={
                                       "max_length": "头像URL长度不能超过200个字符!"
                                   }
                                   )

    nickname = serializers.CharField(max_length=100, help_text="用户昵称", required=False, allow_blank=True,
                                     error_messages={
                                         "max_length": "用户昵称长度不能超过100个字符!"
                                     }
                                     )

    gender = serializers.ChoiceField(choices=GENDER_CHOICES, help_text="性别", required=False, allow_null=True,
                                     error_messages={
                                         "invalid_choice": "性别请选择男或者女!"
                                     }
                                     )

    class Meta:
        model = Users
        fields = ['username', 'verify_key', "verify_value", 'email', 'mobile', 'avatar', "nickname", "gender",
                  "password", "password2"]

    def validate_code(self):
        """
        验证图片验证码
        """
        try:
            # 从数据库中获取验证码对象
            o_captcha = CaptchaStore.objects.get(hashkey=self.initial_data['verify_key'])
            # 计算时间差
            seconds_ago = datetime.now() - timedelta(seconds=CAPTCHA_EXPIRE_TIME)
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

    @staticmethod
    def validate_username(username):
        """
        验证用户名是否已经注册
        """
        try:
            Users.objects.get(username=username)
            raise CustomValidationError("该账号已经注册，请跟换用户名！")
        except Users.DoesNotExist:
            pass
        return username

    @staticmethod
    def validated_mobile(mobile):
        """
        验证手机号是否已经注册
        """
        if not re.match(REGEX_MOBILE, mobile):
            raise CustomValidationError("请输入正确的手机号！")
        try:
            Users.objects.get(mobile=mobile)
            raise CustomValidationError("改手机号已经注册，请跟换手机号！")
        except Users.DoesNotExist:
            pass
        return mobile

    @staticmethod
    def validate_email(email):
        """
        验证邮箱是否已经注册
        """
        try:
            Users.objects.get(email=email)
            raise CustomValidationError("该邮箱已经注册，请跟换邮箱！")
        except Users.DoesNotExist:
            pass
        return email

    def validate_password(self, password):
        """
        验证密码
        :param password: 密码
        """
        password2 = self.initial_data.get('password2', '')
        if len(password) < 6:
            raise CustomValidationError("密码长度至少6位!")
        # 密码强度：至少6-20个字符，至少1个大写字母，1个小写字母和1个数字，其他可以是任意字符
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{6,20}$', password):
            raise CustomValidationError("密码格式不正确(大小写字母、数字组合)")
        if password != password2:
            raise CustomValidationError("两次密码输入不一致!")
        return password

    def validate(self, data):
        """
        自定义验证器
        """
        # 验证图片验证码
        self.validate_code()
        # 验证密码
        self.validate_password(data.get('password', ''))
        # 验证手机号
        self.validate_email(data.get('mobile', ''))
        # 验证邮箱
        self.validate_email(data.get('email', ''))
        # 验证用户名
        self.validate_username(data.get('username', ''))
        return data

    def create(self, validated_data):
        username = validated_data.get('username', '')
        password = validated_data.get('password', "")
        email = validated_data.get('email', '')
        mobile = validated_data.get('mobile', '')
        avatar = validated_data.get('avatar', '')
        nickname = validated_data.get('nickname', '')
        gender = validated_data.get('gender', '')

        user = Users.objects.create(
            username=username,
            password=make_password(password),
            email=email,
            mobile=mobile,
            avatar=avatar,
            nickname=nickname,
            gender=gender,
            identity=2
        )
        # Generate token
        refresh = RefreshToken.for_user(user)
        data = {
            'username': user.username,
            "user_id": user.user_id,
            "avatar": user.avatar,
            "nickname": user.nickname,
            'refresh_token': str(refresh),
            'access_token': str(refresh.access_token)
        }
        return data
