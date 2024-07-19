"""
URL configuration for application project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from user.views.common import CaptchaView  # type: ignore
from user.views.login import LoginView  # type: ignore
from user.views.signup import SignUpView  # type: ignore
from configs.config import openapi_title
# 媒体文件流式响应
from utils.streamingmedia_response import streamingmedia_serve
from django.conf import settings
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from utils.swagger import CustomOpenAPISchemaGenerator
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenRefreshView

schema_view = get_schema_view(
    openapi.Info(
        title=openapi_title,
        default_version='v1',
        # description="Test description",
        # terms_of_service="https://www.google.com/policies/terms/",
        # contact=openapi.Contact(email="contact@snippets.local"),
        # license=openapi.License(name="BSD License"),
    ),
    # public 如果为False，则只包含当前用户可以访问的端点。True返回全部
    public=True,
    permission_classes=(permissions.AllowAny,),  # 可以允许任何人查看该接口
    # permission_classes=(permissions.IsAuthenticated) # 只允许通过认证的查看该接口
    generator_class=CustomOpenAPISchemaGenerator,
)
urlpatterns = [
    # ========================================================================================= #
    # ************************************ 媒体文件相关接口 ************************************* #
    # ========================================================================================= #
    path('static/<path:path>', serve, {'document_root': settings.STATIC_ROOT}, ),  # 处理静态文件
    # path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT},),  # 处理媒体文件
    path('media/<path:path>', streamingmedia_serve, {'document_root': settings.MEDIA_ROOT}, ),  # 处理媒体文件

    # ========================================================================================= #
    # ************************************ 接口文档相关 ************************************* #
    # ========================================================================================= #
    # api文档地址(正式上线需要注释掉)
    re_path(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    re_path(r'^api/djapi(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='api-schema-json'),
    path('api-docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path(r'djangox-redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('admin/', admin.site.urls),

    # ========================================================================================= #
    # ******************************* 用户登录验证码，token相关接口 ******************************** #
    # ========================================================================================= #
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # 刷新token
    path('api/captcha/', CaptchaView.as_view(), name="captcha"),  # 获取图片验证码
    path("api/login/", LoginView.as_view(), name="login"),  # 登录接口
    path("api/signup/", SignUpView.as_view(), name="signup"),  # 注册接口

    # ========================================================================================= #
    # ***********************************  用户模块相关接口  ************************************ #
    # ========================================================================================= #
    path("api/user/", include("user.urls"), name="user"),  # 用户路由分发

    # ========================================================================================= #
    # ***********************************  系统模块相关接口  *********************************** #
    # ========================================================================================= #
    path('api/system/', include('system.urls'), name="system"),  # 系统路由分发
]
