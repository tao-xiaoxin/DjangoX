# -*- coding: utf-8 -*-

"""
@Remark: 自定义序列化器
"""
from rest_framework import serializers
from rest_framework.fields import empty
from rest_framework.request import Request
from rest_framework.serializers import ModelSerializer
from user.models import Users  # type: ignore
from rest_framework_simplejwt.serializers import TokenVerifySerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.settings import api_settings


class CustomModelSerializer(ModelSerializer):
    """
    增强DRF的ModelSerializer,可自动更新模型的审计字段记录
    (1)self.request能获取到rest_framework.request.Request对象
    """
    # 修改人的审计字段名称, 默认modifier, 继承使用时可自定义覆盖
    modifier_field_id = 'modifier'
    modifier_name = serializers.SerializerMethodField(read_only=True)

    def get_modifier_name(self, instance):
        if not hasattr(instance, 'modifier'):
            return None
        queryset = Users.objects.filter(id=instance.modifier).values_list('name', flat=True).first()
        if queryset:
            return queryset
        return None

    # 创建人的审计字段名称, 默认creator, 继承使用时可自定义覆盖
    creator_field_id = 'creator'
    creator_name = serializers.SlugRelatedField(slug_field="name", source="creator", read_only=True)
    # 数据所属部门字段
    dept_belong_id_field_name = 'dept_belong_id'
    # 添加默认时间返回格式
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)

    def __init__(self, instance=None, data=empty, request=None, **kwargs):
        super().__init__(instance, data, **kwargs)
        self.request: Request = request or self.context.get('request', None)

    def save(self, **kwargs):
        return super().save(**kwargs)

    def create(self, validated_data):
        if self.request:
            if str(self.request.user) != "AnonymousUser":
                if self.modifier_field_id in self.fields.fields:
                    validated_data[self.modifier_field_id] = self.get_request_user_id()
                if self.creator_field_id in self.fields.fields:
                    validated_data[self.creator_field_id] = self.request.user
                if self.dept_belong_id_field_name in self.fields.fields and not validated_data.get(
                        self.dept_belong_id_field_name, None):
                    validated_data[self.dept_belong_id_field_name] = getattr(self.request.user, 'dept_id', None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if self.request:
            if str(self.request.user) != "AnonymousUser":
                if self.modifier_field_id in self.fields.fields:
                    validated_data[self.modifier_field_id] = self.get_request_user_id()
            if hasattr(self.instance, self.modifier_field_id):
                setattr(self.instance, self.modifier_field_id, self.get_request_user_id())
        return super().update(instance, validated_data)

    def get_request_username(self):
        if getattr(self.request, 'user', None):
            return getattr(self.request.user, 'username', None)
        return None

    def get_request_name(self):
        if getattr(self.request, 'user', None):
            return getattr(self.request.user, 'name', None)
        return None

    def get_request_user_id(self):
        if getattr(self.request, 'user', None):
            return getattr(self.request.user, 'id', None)
        return None


class TokenRefreshSerializer(serializers.Serializer):
    """
    自定义的令牌刷新序列化器，自定义输出格式
    """
    # 定义一个字符串字段来接收刷新令牌，并添加自定义错误信息
    refresh = serializers.CharField(
        error_messages={
            "blank": "刷新令牌不可以为空!",
            "required": "刷新令牌是必填项!",
        }
    )

    def validate(self, attrs):
        # 使用提供的刷新令牌创建一个新的 RefreshToken 对象
        refresh = RefreshToken(attrs['refresh'])
        refresh_data = {
            'access_token': str(refresh.access_token)
        }
        # 检查是否启用了刷新令牌轮换
        if api_settings.ROTATE_REFRESH_TOKENS:
            # 检查是否在轮换后将旧令牌加入黑名单
            if api_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    # 尝试将给定的刷新令牌加入黑名单
                    refresh.blacklist()
                except AttributeError:
                    # 如果未安装黑名单应用，`blacklist` 方法将不存在
                    # 这种情况下我们简单地跳过黑名单操作
                    pass

            # 为刷新令牌设置新的 JTI (JWT ID)
            refresh.set_jti()
            # 为刷新令牌设置新的过期时间
            refresh.set_exp()

            # 将新的刷新令牌添加到数据字典中
            refresh_data['refresh_token'] = str(refresh)

        # 创建一个包含新的访问令牌的数据字典
        data = {
            "code": 2000,
            "msg": "刷新成功!",
            "data": refresh_data
        }
        # 返回包含新的访问令牌和（如果适用）新的刷新令牌的数据字典
        return data
