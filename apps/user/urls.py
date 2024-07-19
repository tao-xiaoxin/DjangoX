"""
@Remark: 用户模块相关的路由文件
"""
from django.urls import path, re_path
from rest_framework import routers

user_url = routers.SimpleRouter()

urlpatterns = [
    # re_path('operation_log/deletealllogs/',OperationLogViewSet.as_view({'delete':'deletealllogs'})),

]
urlpatterns += user_url.urls
