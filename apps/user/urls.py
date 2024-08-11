"""
@Remark: 用户模块相关的路由文件
"""
from django.urls import path, re_path
from rest_framework import routers
from .views.user import (SetUserNicknameView, ChangeAvatarView, DestroyUserView, ForgetPasswdResetView)
from .views.user import UserManageViewSet

user_url = routers.SimpleRouter()
user_url.register(r'users', UserManageViewSet)

urlpatterns = [
    re_path('disable_user/(?P<pk>.*?)/', UserManageViewSet.as_view({'put': 'disable_user'}), name='后台禁用用户'),
    path('export_users/', UserManageViewSet.as_view({'get': 'export_execl'}), name='导出用户信息'),
    path('restpassword/', ForgetPasswdResetView.as_view(), name='忘记密码重置密码'),
    re_path('user_info/(?P<pk>.*?)/', UserManageViewSet.as_view({"get": "userinfo"}), name='获取用户信息'),
    # 修改用户信息
    re_path('user_info/(?P<pk>.*?)/', UserManageViewSet.as_view({'put': 'update'}), name='修改用户信息'),
    # 用户注销账号
    re_path('destroy_user/', DestroyUserView.as_view(), name='注销用户'),

]
urlpatterns += user_url.urls
