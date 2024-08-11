from django.shortcuts import render
from rest_framework.views import APIView
from utils.image_upload import file_upload
from utils.json_response import DetailResponse, ErrorResponse


# Create your views here.
# 上传图片或文件
class UploadFileView(APIView):
    '''
    上传图片或文件
    post:
    【功能描述】上传图片或文件</br>
    【参数说明】无，需要登录携带token后才能调用</br>
    '''

    def post(self, request, *args, **kwargs):
        result = file_upload(request, "file")
        if result['code'] == 200:
            return DetailResponse(data=result['files'], msg=result['msg'])
        else:
            return ErrorResponse(msg=result['msg'])
