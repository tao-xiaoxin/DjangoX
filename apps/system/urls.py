from django.urls import path, re_path
from rest_framework import routers
from apps.system.views import UploadFileView, OperationLogViewSet, LoginLogViewSet

system_url = routers.SimpleRouter()
system_url.register(r'operation_log', OperationLogViewSet)
system_url.register(r'login_log', LoginLogViewSet)

urlpatterns = [
    re_path('operation_log/deletealllogs/', OperationLogViewSet.as_view({'delete': 'deletealllogs'}),name='清空操作日志'),
    re_path('login_log/deletealllogs/', LoginLogViewSet.as_view({'delete': 'deletealllogs'}), name='清空登录日志'),
    path('uploadfile/', UploadFileView.as_view(), name='上传文件图片'),

]
urlpatterns += system_url.urls
