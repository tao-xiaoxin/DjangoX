from django.shortcuts import render
from rest_framework.views import APIView
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from utils.json_response import SuccessResponse
from captcha.views import CaptchaStore, captcha_image
import base64
# Create your views here.

class CaptchaView(APIView):
    """
    获取图片验证码
    """
    authentication_classes = []

    @swagger_auto_schema(
        responses={
            '200': openapi.Response('获取成功')
        },
        security=[],
        operation_id='captcha-get',
        operation_description='验证码获取',
    )
    def get(self, request):
        hashkey = CaptchaStore.generate_key()
        id = CaptchaStore.objects.filter(hashkey=hashkey).first().id
        imgage = captcha_image(request, hashkey)
        # 将图片转换为base64
        image_base = base64.b64encode(imgage.content)
        json_data = {"key": id, "image_base": "data:image/png;base64," + image_base.decode('utf-8')}
        return SuccessResponse(data=json_data)

