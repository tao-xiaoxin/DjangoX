# -*- coding: utf-8 -*-

"""
@Remark: 用户相关过滤器
"""
import django_filters
from django_filters.rest_framework import FilterSet
from .models import Users


class UsersManageTimeFilter(FilterSet):
    """
    用户管理 简单过滤器
    URL格式：http://127.0.0.1:8000/?start_time=2020-12-02 12:00:00&end_time=2021-12-13 12:00:00
    field_name: 过滤字段名，一般应该对应模型中字段名
    lookup_expr: 查询时所要进行的操作，和ORM中运算符一致
    fields：指明过滤字段，可以是列表，列表中字典可以过滤，默认是判等；也可以字典，字典可以自定义操作
    exclude = ['password'] 排除字段，不允许使用列表中字典进行过滤
    自定义字段名可以和模型中不一致，但一定要用参数field_name指明对应模型中的字段名
    """
    # 开始时间
    start_time = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='gte')  # 指定过滤的字段
    # 结束时间
    end_time = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='lte')
    # 模糊搜索
    username = django_filters.CharFilter(field_name='username', lookup_expr='icontains')  # icontains表示该字段模糊搜索
    # 模糊搜索
    nickname = django_filters.CharFilter(field_name='nickname', lookup_expr='icontains')  # icontains表示该字段模糊搜索
    # 模糊搜索
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')  # icontains表示该字段模糊搜索
    # 模糊搜索
    mobile = django_filters.CharFilter(field_name='mobile', lookup_expr='icontains')  # icontains表示该字段模糊搜索
    is_active = django_filters.CharFilter(field_name='is_active')  # icontains表示该字段模糊搜索

    class Meta:
        model = Users
        fields = ['start_time', 'end_time', 'username', 'mobile', 'is_active', 'nickname', 'name']
