"""
@Remark: 用户模块相关的路由文件
"""
from django.urls import path, re_path
from rest_framework import routers
from .views.user import DestroyUserView, ForgetPasswdResetView
from .views.user import UserManageViewSet, UserCenterViewSet

user_url = routers.SimpleRouter()
user_url.register(r'users', UserManageViewSet)

urlpatterns = [
    # ========================================================================================= #
    # ***********************************  用户后台管理相关接口  *********************************** #
    # ========================================================================================= #
    re_path('disable_user/(?P<pk>.*?)/', UserManageViewSet.as_view({'put': 'disable_user'}), name='后台禁用用户'),
    path('export/', UserManageViewSet.as_view({'get': 'export'}), name='导出用户信息'),
    path('restpassword/', ForgetPasswdResetView.as_view(), name='忘记密码重置密码'),


    # ========================================================================================= #
    # ***********************************  用户个人中心相关接口  *********************************** #
    # ========================================================================================= #
    re_path('destroy_user/', DestroyUserView.as_view(), name='用户注销账号'),
    path('center/info/', UserCenterViewSet.as_view({"get": "me"}), name='用户个人中心获取个人信息'),
    path('center/nickname/', UserCenterViewSet.as_view({"post": "set_nickname"}), name='用户个人中心修改昵称'),
    # 修改手机号
    path('center/mobile/', UserCenterViewSet.as_view({"post": "change_mobile"}), name='用户个人中心修改密码'),
    # 修改邮箱
    path('center/email/', UserCenterViewSet.as_view({"post": "change_email"}), name='用户个人中心修改邮箱'),
    # 修改头像
    path('center/avatar/', UserCenterViewSet.as_view({"post": "change_avatar"}), name='用户个人中心修改头像'),
]
urlpatterns += user_url.urls
