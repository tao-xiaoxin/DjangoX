from django.shortcuts import render
from rest_framework.views import APIView
from utils.file_upload import file_upload
from utils.json_response import DetailResponse, ErrorResponse
from .models import OperationLog, LoginLog
from utils.serializers import CustomModelSerializer
from utils.viewset import CustomModelViewSet
from utils.json_response import SuccessResponse, ErrorResponse
from .filters import OperationLogTimeFilter, LoginLogTimeFilter
from .serializers import OperationLogSerializer, LoginLogSerializer


# Create your views here.
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


class OperationLogViewSet(CustomModelViewSet):
    """
    操作日志接口
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    queryset = OperationLog.objects.all().order_by('-create_time')
    serializer_class = OperationLogSerializer
    # filterset_fields = '__all__'
    filterset_class = OperationLogTimeFilter
    search_fields = ('request_modular', 'request_path', 'request_ip', 'request_os', 'request_body')

    def deletealllogs(self, request):
        user = request.user
        if user.identity in [0, 1]:
            OperationLog.objects.all().delete()
            return SuccessResponse(msg="清空成功")
        return ErrorResponse(msg="您没有权限执行此操作，需要超级管理员权限")


class LoginLogViewSet(CustomModelViewSet):
    """
    登录日志接口
    list: 查询
    create: 新增
    update: 修改
    retrieve: 单例
    destroy: 删除
    """
    queryset = LoginLog.objects.all().order_by('-create_time')
    serializer_class = LoginLogSerializer
    filterset_class = LoginLogTimeFilter
    search_fields = ('username', 'ip', 'browser', 'os', 'agent')

    def deletealllogs(self, request):
        user = request.user
        if user.identity in [0, 1]:  # 假设 0 和 1 代表超级管理员权限
            LoginLog.objects.all().delete()
            return SuccessResponse(msg="清空成功")
        return ErrorResponse(msg="您没有权限执行此操作，需要超级管理员权限")
