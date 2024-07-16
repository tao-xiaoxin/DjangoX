import base64
from datetime import datetime, timedelta
from captcha.views import CaptchaStore, captcha_image
from django.utils.translation import gettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.hashers import make_password
from . import models
from utils.json_response import SuccessResponse, ErrorResponse
from utils.validator import CustomValidationError
# from utils.request_util import save_login_log
from django_redis import get_redis_connection
from django.conf import settings
from configs.config import IS_SINGLE_TOKEN
from rest_framework import serializers
from utils.validator import CustomUniqueValidator
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
# Create your views here.

class CaptchaView(APIView):
    """
    获取图片验证码
    """
    authentication_classes = []

    @swagger_auto_schema(
        responses={
            '200': openapi.Response('获取成功')
        },
        security=[],
        operation_id='captcha-get',
        operation_description='验证码获取',
    )
    def get(self, request):
        hashkey = CaptchaStore.generate_key()
        id = CaptchaStore.objects.filter(hashkey=hashkey).first().id
        imgage = captcha_image(request, hashkey)
        # 将图片转换为base64
        image_base = base64.b64encode(imgage.content)
        json_data = {"key": id, "image_base": "data:image/png;base64," + image_base.decode('utf-8')}
        return SuccessResponse(data=json_data)


class LoginSerializer(TokenObtainPairSerializer):
    """
    登录的序列化器:
    重写djangorestframework-simplejwt的序列化器
    """
    captcha = serializers.CharField(max_length=6)

    class Meta:
        model = models.Users
        fields = "__all__"
        read_only_fields = ["id"]

    default_error_messages = {
        'no_active_account': _('该账号已被禁用,请联系管理员')
    }

    # 开启验证码验证
    def validate_captcha(self, captcha):
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

    def validate(self, attrs):
        username = attrs['username']
        password = attrs['password']
        user = models.Users.objects.filter(username=username).first()

        if not user:
            result = {
                "code": 4000,
                "msg": "账号/密码不正确",
                "data": None
            }
            return result

        if user and not user.is_staff:  # 判断是否允许登录后台
            result = {
                "code": 4000,
                "msg": "您没有权限登录后台",
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
            data['userId'] = self.user.id
            data['refresh'] = str(refresh)
            data['access'] = str(refresh.access_token)
            request = self.context.get('request')
            request.user = self.user
            # 记录登录成功日志
            save_login_log(request=request)
            # 缓存用户的jwt token
            if IS_SINGLE_TOKEN:
                redis_conn = get_redis_connection("singletoken")
                k = "lybbn-single-token{}".format(user.id)
                TOKEN_EXPIRE_CONFIG = getattr(settings, 'SIMPLE_JWT', None)
                if TOKEN_EXPIRE_CONFIG:
                    TOKEN_EXPIRE = TOKEN_EXPIRE_CONFIG['ACCESS_TOKEN_LIFETIME']
                    redis_conn.set(k, data['access'], TOKEN_EXPIRE)
            result = {
                "code": 2000,
                "msg": "请求成功",
                "data": data
            }
        else:
            result = {
                "code": 4000,
                "msg": "账号/密码不正确",
                "data": None
            }
        return result


class LoginView(TokenObtainPairView):
    """
    登录接口
    """
    serializer_class = LoginSerializer
    permission_classes = []



# class UserSerializer(CustomModelSerializer):
#     """
#     用户管理-序列化器
#     """
#     rolekey = serializers.SerializerMethodField(read_only=True)  # 新增自定义字段
#
#     def get_rolekey(self,obj):
#         queryset = Role.objects.filter(users__id=obj.id).values_list('key',flat=True)
#         return queryset
#
#     class Meta:
#         model = Users
#         read_only_fields = ["id"]
#         exclude = ['password']
#         extra_kwargs = {
#             'post': {'required': False},
#         }
#
#
# class UserCreateSerializer(CustomModelSerializer):
#     """
#     管理员用户新增-序列化器
#     """
#     username = serializers.CharField(max_length=50,validators=[CustomUniqueValidator(queryset=Users.objects.all(), message="账号必须唯一")])
#     password = serializers.CharField(required=False, default=make_password("123456"))
#
#     is_staff = serializers.BooleanField(required=False,default=True)#是否允许登录后台
#
#     def create(self, validated_data):
#         if "password" in validated_data.keys():
#             if validated_data['password']:
#                 validated_data['password'] = make_password(validated_data['password'])
#         validated_data['identity'] = 1
#         return super().create(validated_data)
#
#     def save(self, **kwargs):
#         data = super().save(**kwargs)
#         data.post.set(self.initial_data.get('post', []))
#         return data
#
#     class Meta:
#         model = Users
#         fields = "__all__"
#         read_only_fields = ["id"]
#         extra_kwargs = {
#             'post': {'required': False},
#         }
#
#
# class UserUpdateSerializer(CustomModelSerializer):
#     """
#     用户修改-序列化器
#     """
#     username = serializers.CharField(max_length=50,validators=[CustomUniqueValidator(queryset=Users.objects.all(), message="账号必须唯一")])
#     password = serializers.CharField(required=False, allow_blank=True)
#
#     def update(self, instance, validated_data):
#         if "password" in validated_data.keys():
#             if validated_data['password']:
#                 validated_data['password'] = make_password(validated_data['password'])
#         return super().update(instance,validated_data)
#
#     def save(self, **kwargs):
#         data = super().save(**kwargs)
#         data.post.set(self.initial_data.get('post', []))
#         return data
#
#     class Meta:
#         model = Users
#         read_only_fields = ["id"]
#         fields = "__all__"
#         extra_kwargs = {
#             'post': {'required': False, 'read_only': True},
#         }
#
#
# class UserViewSet(CustomModelViewSet):
#     """
#     后台管理员用户接口:
#     """
#     queryset = Users.objects.filter(identity=1,is_delete=False).order_by('-create_datetime')
#     serializer_class = UserSerializer
#     create_serializer_class = UserCreateSerializer
#     update_serializer_class = UserUpdateSerializer
#     # filterset_fields = ('name','is_active','username')
#     filterset_class = UsersManageTimeFilter
#
#     def user_info(self,request):
#         """获取当前用户信息"""
#         user = request.user
#         result = {
#             "name":user.name,
#             "mobile":user.mobile,
#             "gender":user.gender,
#             "email":user.email
#         }
#         return SuccessResponse(data=result,msg="获取成功")
#
#     def update_user_info(self,request):
#         """修改当前用户信息"""
#         user = request.user
#         Users.objects.filter(id=user.id).update(**request.data)
#         return SuccessResponse(data=None, msg="修改成功")
#
#
#     def change_password(self,request,*args, **kwargs):
#         """密码修改"""
#         user = request.user
#         instance = Users.objects.filter(id=user.id,identity__in=[0,1]).first()
#         data = request.data
#         old_pwd = data.get('oldPassword')
#         new_pwd = data.get('newPassword')
#         new_pwd2 = data.get('newPassword2')
#         if instance:
#             if new_pwd != new_pwd2:
#                 return ErrorResponse(msg="2次密码不匹配")
#             elif instance.check_password(old_pwd):
#                 instance.password = make_password(new_pwd)
#                 instance.save()
#                 return SuccessResponse(data=None, msg="修改成功")
#             else:
#                 return ErrorResponse(msg="旧密码不正确")
#         else:
#             return ErrorResponse(msg="未获取到用户")
