from django.urls import path, re_path
from rest_framework import routers
from .views import UploadFileView
system_url = routers.SimpleRouter()

urlpatterns = [
    # re_path('operation_log/deletealllogs/',OperationLogViewSet.as_view({'delete':'deletealllogs'})),
    path('uploadfile/', UploadFileView.as_view(), name='上传文件图片'),

]
urlpatterns += system_url.urls
