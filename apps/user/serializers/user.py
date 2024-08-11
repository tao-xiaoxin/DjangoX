from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from utils.serializers import CustomModelSerializer
from ..models import Users


class UserManageSerializer(CustomModelSerializer):
    """
    用户管理-序列化器
    """

    class Meta:
        model = Users
        read_only_fields = ["user_id"]
        exclude = ['password']


class UserManageCreateSerializer(CustomModelSerializer):
    """
    用户管理-序列化器
    """

    # 新增重写
    def create(self, validated_data):
        if "password" in validated_data.keys():
            if validated_data['password']:
                validated_data['password'] = make_password(validated_data['password'])
        validated_data['identity'] = 2
        return super().create(validated_data)

    class Meta:
        model = Users
        fields = "__all__"
        read_only_fields = ["user_id"]
        extra_kwargs = {'password': {'required': False}, }


class UserManageUpdateSerializer(CustomModelSerializer):
    """
    用户管理-序列化器
    """

    # 更新重写
    def update(self, instance, validated_data):
        if "password" in validated_data.keys():
            if validated_data['password']:
                validated_data['password'] = make_password(validated_data['password'])
            else:
                validated_data.pop('password', None)
        return super().update(instance, validated_data)

    class Meta:
        model = Users
        fields = '__all__'
        read_only_fields = ["user_id"]
        extra_kwargs = {
            'password': {'required': False},
        }


class ExportUserManageSerializer(CustomModelSerializer):
    """
    导出 用户信息 简单序列化器
    """
    is_active_name = serializers.SerializerMethodField()

    class Meta:
        model = Users
        fields = ('user_id', 'nickname', 'mobile', 'is_active_name', 'create_time')

    @staticmethod
    def get_is_active_name(obj):
        if obj.is_active:
            return "正常"
        else:
            return "禁用"
