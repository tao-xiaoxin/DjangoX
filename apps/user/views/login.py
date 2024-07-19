from rest_framework_simplejwt.views import TokenObtainPairView
from ..serializers.login_serializer import LoginSerializer


# Create your views here.
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
