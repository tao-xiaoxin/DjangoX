from django.shortcuts import render
from rest_framework.views import APIView
from utils.json_response import SuccessResponse, ErrorResponse, DetailResponse
from utils.common import get_parameter_dict, getRandomSet, REGEX_MOBILE
import re
from django.db.models import Q, F, Sum
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from rest_framework_simplejwt.authentication import JWTAuthentication
from utils.serializers import CustomModelSerializer
from utils.viewset import CustomModelViewSet
from rest_framework.permissions import IsAuthenticated
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from utils.validator import CustomValidationError
from ..models import Users
from ..filters import UsersManageTimeFilter
from django.contrib.auth.hashers import make_password
from utils.export_excel import export_excel
from django.db import transaction
from ..serializers.user import (UserManageSerializer, UserManageCreateSerializer, UserManageUpdateSerializer,
                                ExportUserManageSerializer)
from rest_framework import viewsets
from utils.file_upload import file_upload


# Create your views here.


class UserManageViewSet(CustomModelViewSet):
    """
    后台用户管理
    """
    queryset = Users.objects.order_by("-create_time")
    serializer_class = UserManageSerializer
    create_serializer_class = UserManageCreateSerializer
    update_serializer_class = UserManageUpdateSerializer
    filterset_class = UsersManageTimeFilter

    @staticmethod
    def disable_user(request, *args, **kwargs):
        """禁用用户"""
        instance = Users.objects.filter(user_id=kwargs.get('pk')).first()
        if instance:
            if instance.is_active:
                instance.is_active = False
            else:
                instance.is_active = True
            instance.save()
            return DetailResponse(data=None, msg="修改成功！")
        else:
            return ErrorResponse(msg="未获取到用户！")

    def export(self, request):
        """
        导出用户数据
        """
        field_data = ['用户ID', '昵称', '手机号', '状态', '创建时间']
        queryset = self.filter_queryset(self.get_queryset())
        data = ExportUserManageSerializer(queryset, many=True).data
        return SuccessResponse(data=export_excel(request, field_data, data, '用户数据.xls'), msg='success')


class UserCenterViewSet(viewsets.GenericViewSet):
    """
    前端用户个人中心
    """
    queryset = Users.objects.all()
    serializer_class = UserManageSerializer

    def get_object(self):
        return self.request.user

    def me(self, request):
        """
        获取当前登录用户的信息
        """
        serializer = self.get_serializer(self.get_object())
        return DetailResponse(serializer.data)

    def set_nickname(self, request):
        """
        修改昵称
        """
        nickname = get_parameter_dict(request).nickname
        if nickname is None:
            return ErrorResponse(msg="昵称不能为空！")
        if not isinstance(nickname, str):
            return ErrorResponse(msg='类型错误！')
        user = self.get_object()
        user.nickname = nickname
        user.save()
        return SuccessResponse(msg="success")

    def change_avatar(self, request):
        """
        头像修改
        """
        result = file_upload(request, "avatar")
        if result['code'] == 200:
            user = self.get_object()
            user.avatar = result['files'][0]
            user.save()
            return SuccessResponse(data=result['files'], msg=result['msg'])
        else:
            return ErrorResponse(msg=result['msg'])

    def change_mobile(self, request):
        """
        修改手机号
        """
        mobile = get_parameter_dict(request).mobile
        if not re.match(REGEX_MOBILE, mobile):
            return ErrorResponse(msg="手机号格式不正确！")
        try:
            Users.objects.get(mobile=mobile)
            return ErrorResponse(msg="该手机号已经注册，请跟换手机号！")
        except Users.DoesNotExist:
            pass
        user = self.get_object()
        user.mobile = mobile
        user.save()
        return SuccessResponse(msg="success")

    def change_email(self, request):
        """
        修改邮箱
        """
        email = get_parameter_dict(request).email
        if not email:
            return ErrorResponse(msg="邮箱不能为空！")
        try:
            Users.objects.get(email=email)
            return ErrorResponse(msg="该邮箱已经注册，请跟换邮箱！")
        except Users.DoesNotExist:
            pass
        user = self.get_object()
        user.email = email
        user.save()
        return SuccessResponse(msg="success")


class DestroyUserView(APIView):
    '''
    注销账号(标记已注销)
    post:
    【功能描述】注销账号(标记已注销)</br>
    '''
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        if user.identity in [0, 1]:
            return ErrorResponse(msg="该用户不支持注销!")
        if '(已注销)' in user.username:
            return ErrorResponse(msg="该用户已注销或不支持注销!")
        with transaction.atomic():
            randstr = getRandomSet(6)
            user.username = user.username + "(已注销)" + randstr
            user.mobile = user.mobile + "(已注销)" + randstr
            user.is_delete = True
            user.is_active = False
            user.save()
            return DetailResponse(msg="success")


class ForgetPasswdResetView(APIView):
    '''
    post:
    【功能描述】根据邮箱重置用户密码</br>
    【参数说明】mobile为手机号</br>
    【参数说明】password为密码</br>
    '''
    authentication_classes = []
    permission_classes = []

    @staticmethod
    def validate_email(email):
        """
        验证邮箱是否合法
        :param email: 邮箱
        """
        if not email:
            raise CustomValidationError("邮箱不能为空!")
        if not re.match(r'^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$', email):
            raise CustomValidationError("邮箱格式不正确!")
        return email

    @staticmethod
    def validate_password(password, password2):
        """
        验证密码
        :param password: 密码
        :param password2: 确认密码
        """
        if not password or not password2:
            raise CustomValidationError("密码不能为空!")
        if len(password) < 6:
            raise CustomValidationError("密码长度至少6位!")
        # 密码强度：至少6-20个字符，至少1个大写字母，1个小写字母和1个数字，其他可以是任意字符
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{6,20}$', password):
            raise CustomValidationError("密码格式不正确(大小写字母、数字组合)")
        if password != password2:
            raise CustomValidationError("两次密码输入不一致!")
        return password

    def post(self, request, *args, **kwargs):

        email = get_parameter_dict(request).email
        password = get_parameter_dict(request).password
        password2 = get_parameter_dict(request).password2
        # 验证邮箱
        email = self.validate_email(email)
        # 验证密码
        password = self.validate_password(password, password2)
        # 开始更换密码
        user = Users.objects.filter(email=email, identity=2).first()
        if not user:
            return ErrorResponse(msg="用户不存在")
        if not user.is_active:
            return ErrorResponse(msg="该账号已被禁用，请联系管理员")
        # 重置密码
        user.password = make_password(password)
        user.save()
        return DetailResponse(msg="密码重置成功！")
