"""
@Remark: 用户模块相关的路由文件
"""
from django.urls import path, re_path
from rest_framework import routers
from .views.user import (SetUserNicknameView, ChangeAvatarView, uploadImagesView, DestroyUserView,ForgetPasswdResetView)
from .views.user import UserManageViewSet

user_url = routers.SimpleRouter()
user_url.register(r'users', UserManageViewSet)

urlpatterns = [
    # re_path('operation_log/deletealllogs/',OperationLogViewSet.as_view({'delete':'deletealllogs'})),
    re_path('users/disableuser/(?P<pk>.*?)/', UserManageViewSet.as_view({'put': 'disableuser'}), name='后台禁用用户'),
    path('users/exportexecl/', UserManageViewSet.as_view({'get': 'exportexecl'}), name='后台导出数据'),
    path('api/app/restpassword/', ForgetPasswdResetView.as_view(), name='app端手机号重置密码'),
    path('api/app/setnickname/', SetUserNicknameView.as_view(), name='app端修改昵称'),
    path('api/app/changeavatar/', ChangeAvatarView.as_view(), name='app端回收员修改头像'),
    path('api/app/uploadimage/', uploadImagesView.as_view(), name='app端上传图片'),
    # path('api/xcx/getuserinfo/', XCXWeChatUserInfoUpdateAPIView.as_view(), name='微信小程序获取用户信息'),

]
urlpatterns += user_url.urls
