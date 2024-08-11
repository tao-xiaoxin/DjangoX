"""
@Remark: 用户模块相关的路由文件
"""
from django.urls import path, re_path
from rest_framework import routers
from .views.user import (SetUserNicknameView, ChangeAvatarView, DestroyUserView,ForgetPasswdResetView)
from .views.user import UserManageViewSet

user_url = routers.SimpleRouter()
user_url.register(r'users', UserManageViewSet)

urlpatterns = [
    # re_path('operation_log/deletealllogs/',OperationLogViewSet.as_view({'delete':'deletealllogs'})),
    re_path('disableuser/(?P<pk>.*?)/', UserManageViewSet.as_view({'put': 'disableuser'}), name='后台禁用用户'),
    path('export_users/', UserManageViewSet.as_view({'get': 'exportexecl'}), name='导出用户信息'),
    path('restpassword/', ForgetPasswdResetView.as_view(), name='忘记密码重置密码'),
    # path('api/app/setnickname/', SetUserNicknameView.as_view(), name='app端修改昵称'),
    # path('api/app/changeavatar/', ChangeAvatarView.as_view(), name='app端回收员修改头像'),

    # path('api/xcx/getuserinfo/', XCXWeChatUserInfoUpdateAPIView.as_view(), name='微信小程序获取用户信息'),

]
urlpatterns += user_url.urls
