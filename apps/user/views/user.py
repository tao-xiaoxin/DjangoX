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
from utils.filters import UsersManageTimeFilter
from django.contrib.auth.hashers import make_password
from utils.export_excel import export_excel
from django.db import transaction


# Create your views here.


class UserManageViewSet(CustomModelViewSet):
    """
    后台用户管理 接口:
    """
    queryset = Users.objects.filter(identity=2).order_by("-create_time")  # 排除管理员
    # serializer_class = UserManageSerializer
    # create_serializer_class = UserManageCreateSerializer
    # update_serializer_class = UserManageUpdateSerializer
    filterset_class = UsersManageTimeFilter

    def disableuser(self, request, *args, **kwargs):
        """禁用用户"""
        instance = Users.objects.filter(user_id=kwargs.get('pk')).first()
        if instance:
            if instance.is_active:
                instance.is_active = False
            else:
                instance.is_active = True
            instance.save()
            return SuccessResponse(data=None, msg="修改成功")
        else:
            return ErrorResponse(msg="未获取到用户")

    def exportexecl(self, request):
        field_data = ['主键', '昵称', '手机号', '状态', '创建时间']
        queryset = self.filter_queryset(self.get_queryset())
        data = ExportUserManageSerializer(queryset, many=True).data
        return SuccessResponse(data=export_excel(request, field_data, data, '用户数据.xls'), msg='success')


# ================================================= #
# ************** 前端用户中心 view  ************** #
# ================================================= #

class SetUserNicknameView(APIView):
    """
    修改昵称
    post:
    修改昵称
    【参数】nickname:需要修改的用户新昵称
    """

    # api文档参数

    @swagger_auto_schema(operation_summary='app回收员修改昵称',
                         # manual_parameters=[#GET请求需要
                         #     # openapi.Parameter("nickname", openapi.IN_QUERY, description="要修改昵称", type=openapi.TYPE_STRING)
                         # ],
                         request_body=openapi.Schema(  # POST请求需要
                             type=openapi.TYPE_OBJECT,
                             required=['nickname'],
                             properties={
                                 'nickname': openapi.Schema(type=openapi.TYPE_STRING, description="要修改昵称"),
                             },
                         ),
                         responses={200: 'success'},
                         )
    def post(self, request):
        nickname = get_parameter_dict(request)['nickname']
        if nickname is None:
            return ErrorResponse(msg="昵称不能为空")
        if not isinstance(nickname, str):
            return ErrorResponse(msg='类型错误')
        user = request.user
        user.nickname = nickname
        user.save()
        return SuccessResponse(msg="success")


# 前端app头像修改
class ChangeAvatarView(APIView):
    '''
    前端app头像修改
    post:
    【功能描述】前端app头像修改</br>
    【参数说明】无，需要登录携带token后才能调用</br>
    '''
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        result = ImageUpload(request, "avatar")
        if result['code'] == 200:
            user = request.user
            user.avatar = result['img'][0]
            user.save()
            return SuccessResponse(data=result['img'], msg=result['msg'])
        else:
            return ErrorResponse(msg=result['msg'])


# 注销账号(标记已注销)
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
            return ErrorResponse(msg="该用户不支持注销")
        if '(已注销)' in user.username:
            return ErrorResponse(msg="该用户已注销或不支持注销")
        with transaction.atomic():
            randstr = getRandomSet(6)
            user.username = user.username + "(已注销)" + randstr
            user.mobile = user.mobile + "(已注销)" + randstr
            user.is_delete = True
            user.is_active = False
            user.save()
            return SuccessResponse(data={}, msg="success")


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
