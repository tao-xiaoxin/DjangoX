from datetime import datetime, timedelta

from captcha.models import CaptchaStore
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django_redis import get_redis_connection

from utils.validator import CustomValidationError
from ..models import Users
from utils.common import REGEX_MOBILE
import re


class SignUpSerializer(serializers.Serializer):
    mobile = serializers.CharField(required=True)
    code = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    password2 = serializers.CharField(required=True)
    user_name = serializers.CharField(
        required=True,
        error_messages={'required': 'User name is required.'}
    )
    email = serializers.EmailField(
        required=True,
        error_messages={'required': 'Email is required.'}
    )

    class Meta:
        model = Users
        fields = ('user_name', 'email', 'password')

    def validate_code(self, captcha):
        self.image_code = CaptchaStore.objects.filter(id=self.initial_data['captchaKey']).first()
        five_minute_ago = datetime.now() - timedelta(hours=0, minutes=5, seconds=0)
        if self.image_code and five_minute_ago > self.image_code.expiration:
            self.image_code and self.image_code.delete()
            raise CustomValidationError('验证码过期')
        else:
            if self.image_code and (self.image_code.response == captcha or self.image_code.challenge == captcha):
                self.image_code and self.image_code.delete()
            else:
                self.image_code and self.image_code.delete()
                raise CustomValidationError("图片验证码错误")

    @staticmethod
    def validate_mobile(value):
        if not re.match(REGEX_MOBILE, value):
            raise serializers.ValidationError("请输入正确的手机号")
        return value

    def validate_password(self, value):
        if len(value) < 6:
            raise CustomValidationError("密码长度至少6位")
        if not re.match(r'^[a-zA-Z0-9]{6,20}$', value):
            raise CustomValidationError("密码格式不正确(大小写字母、数字组合)")
        return value

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("两次密码输入不一致")
        # 验证短信验证码
        redis_conn = get_redis_connection('verify_codes')
        send_flag = redis_conn.get(f'sms_{data["mobile"]}')
        if not send_flag or send_flag.decode() != data['code']:
            raise serializers.ValidationError("验证码错误或已过期")
        return data

    def create(self, validated_data):
        mobile = validated_data['mobile']
        password = validated_data['password']
        user = Users.objects.create(
            username=mobile,
            password=make_password(password),
            mobile=mobile,
            is_staff=False,
            identity=2
        )
        return user
