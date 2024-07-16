# -*- coding: utf-8 -*-

"""
@Remark: 公共基础model类
"""
import uuid

from django.apps import apps

from django.db import models

from application import settings


def make_uuid():
    # .hex 将生成的uuid字符串中的 － 删除，带-是36位字符，不带-是32位随机字符串
    return str(uuid.uuid4().hex)


class CoreModel(models.Model):
    """
    核心标准抽象模型模型,可直接继承使用
    增加审计字段, 覆盖字段时, 字段名称请勿修改, 必须统一审计字段名称
    """

    id = models.CharField(max_length=100, primary_key=True, default=make_uuid, help_text="Id", verbose_name="Id")
    description = models.CharField(max_length=100, verbose_name="描述", null=True, blank=True, help_text="描述")
    creator = models.ForeignKey(to=settings.AUTH_USER_MODEL, related_query_name='creator_query', null=True,
                                verbose_name='创建人', help_text="创建人", on_delete=models.SET_NULL,
                                db_constraint=False)
    modifier = models.CharField(max_length=100, null=True, blank=True, help_text="修改人", verbose_name="修改人")
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True, help_text="修改时间",
                                       verbose_name="修改时间")
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True, help_text="创建时间",
                                       verbose_name="创建时间")
    is_delete = models.BooleanField(default=False, verbose_name='是否删除', help_text='是否删除')

    class Meta:
        abstract = True
        verbose_name = '核心模型'
        verbose_name_plural = verbose_name


class BaseModel(models.Model):
    """
        基本模型,可直接继承使用，一般不需要使用审计字段的模型可以使用
        覆盖字段时, 字段名称请勿修改
    """
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True, verbose_name='更新时间')
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name='创建时间')
    is_delete = models.BooleanField(default=False, verbose_name='是否删除', help_text='是否删除')

    class Meta:
        abstract = True  # 表示该类是一个抽象类，只用来继承，不参与迁移操作
        verbose_name = '基本模型'
        verbose_name_plural = verbose_name


def get_all_models_objects(model_name=None):
    """
    获取所有 models 对象
    :return: {}
    """
    settings.ALL_MODELS_OBJECTS = {}
    if not settings.ALL_MODELS_OBJECTS:
        all_models = apps.get_models()
        for item in list(all_models):
            table = {
                "tableName": item._meta.verbose_name,
                "db_table": item._meta.db_table,
                "table": item.__name__,
                "tableFields": []
            }
            for field in item._meta.fields:
                fields = {
                    "title": field.verbose_name,
                    "field": field.name
                }
                table['tableFields'].append(fields)
            settings.ALL_MODELS_OBJECTS.setdefault(item.__name__, {"table": table, "object": item})
    if model_name:
        return settings.ALL_MODELS_OBJECTS[model_name] or {}
    return settings.ALL_MODELS_OBJECTS or {}
