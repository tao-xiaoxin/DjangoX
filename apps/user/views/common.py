import base64
from datetime import datetime, timedelta
from captcha.views import CaptchaStore, captcha_image
from captcha.helpers import captcha_image_url
from django.utils.translation import gettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.hashers import make_password
from ..models import models
from utils.json_response import SuccessResponse, ErrorResponse,DetailResponse
from utils.validator import CustomValidationError
# from utils.request_util import save_login_log
from django_redis import get_redis_connection
from django.conf import settings
from rest_framework import serializers
from utils.validator import CustomUniqueValidator
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q


class CaptchaRefresh(APIView):
    """
    获取/刷新 图片验证码
    """
    authentication_classes = []

    @swagger_auto_schema(
        responses={
            '200': openapi.Response('获取成功')
        },
        security=[],
        operation_id='captcha-get',
        operation_description='获取/刷新图片验证码',
    )
    def get(self, request):
        hash_key = CaptchaStore.generate_key()
        img = captcha_image(request, hash_key)
        # 将图片转换为base64
        image_base = base64.b64encode(img.content)
        json_data = {
            "key": hash_key,
            "image_base": "data:image/png;base64," + image_base.decode('utf-8'),
            "image_url": f"{captcha_image_url(hash_key)}",
        }
        return DetailResponse(data=json_data)
