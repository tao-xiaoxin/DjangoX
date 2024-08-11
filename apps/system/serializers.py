# -*- coding: utf-8 -*-

"""
@Remark: 系统相关序列化器
"""
from .models import LoginLog, OperationLog
from utils.serializers import CustomModelSerializer


class OperationLogSerializer(CustomModelSerializer):
    """
    操作日志-序列化器
    """

    class Meta:
        model = OperationLog
        fields = "__all__"
        read_only_fields = ["id"]


class LoginLogSerializer(CustomModelSerializer):
    """
    登录日志-序列化器
    """

    class Meta:
        model = LoginLog
        fields = "__all__"
        read_only_fields = ["id"]
