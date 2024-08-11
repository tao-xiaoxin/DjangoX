# -*- coding: utf-8 -*-

"""
@Remark: 自定义过滤器
"""

import operator
from functools import reduce
import django_filters
import six
from django.db.models import Q
from django.db.models.constants import LOOKUP_SEP
from django_filters import utils
from django_filters.filters import CharFilter
from django_filters.rest_framework import DjangoFilterBackend
from django_filters.rest_framework import FilterSet
# from system.models import OperationLog  # type: ignore
from user.models import Users  # type: ignore


class CustomDjangoFilterBackend(DjangoFilterBackend):
    lookup_prefixes = {
        '^': 'istartswith',
        '=': 'iexact',
        '@': 'search',
        '$': 'iregex',
        '~': 'icontains'
    }

    def construct_search(self, field_name):
        lookup = self.lookup_prefixes.get(field_name[0])
        if lookup:
            field_name = field_name[1:]
        else:
            lookup = 'icontains'
        return LOOKUP_SEP.join([field_name, lookup])

    def find_filter_lookups(self, orm_lookups, search_term_key):
        for lookup in orm_lookups:
            if lookup.find(search_term_key) >= 0:
                return lookup
        return None

    def filter_queryset(self, request, queryset, view):
        filterset = self.get_filterset(request, queryset, view)
        if filterset is None:
            return queryset
        if filterset.__class__.__name__ == 'AutoFilterSet':
            queryset = filterset.queryset
            orm_lookups = []
            for search_field in filterset.filters:
                if isinstance(filterset.filters[search_field], CharFilter):
                    orm_lookups.append(self.construct_search(six.text_type(search_field)))
                else:
                    orm_lookups.append(search_field)
            conditions = []
            queries = []
            for search_term_key in filterset.data.keys():
                orm_lookup = self.find_filter_lookups(orm_lookups, search_term_key)
                if not orm_lookup:
                    continue
                query = Q(**{orm_lookup: filterset.data[search_term_key]})
                queries.append(query)
            if len(queries) > 0:
                conditions.append(reduce(operator.and_, queries))
                queryset = queryset.filter(reduce(operator.and_, conditions))
                return queryset
            else:
                return queryset

        if not filterset.is_valid() and self.raise_exception:
            raise utils.translate_validation(filterset.errors)
        return filterset.qs




# class OperationLogTimeFilter(FilterSet):
#     """
#     日志管理 简单过滤器
#     URL格式：http://127.0.0.1:8000/?start_time=2020-12-02 12:00:00&end_time=2021-12-13 12:00:00
#     field_name: 过滤字段名，一般应该对应模型中字段名
#     lookup_expr: 查询时所要进行的操作，和ORM中运算符一致
#     fields：指明过滤字段，可以是列表，列表中字典可以过滤，默认是判等；也可以字典，字典可以自定义操作
#     exclude = ['password'] 排除字段，不允许使用列表中字典进行过滤
#     自定义字段名可以和模型中不一致，但一定要用参数field_name指明对应模型中的字段名
#     """
#     # 开始时间
#     start_time = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='gte')  # 指定过滤的字段
#     # 结束时间
#     end_time = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='lte')
#     # 模糊搜索
#     request_modular = django_filters.CharFilter(field_name='request_modular',
#                                                 lookup_expr='icontains')  # icontains表示该字段模糊搜索
#     # 模糊搜索
#     request_path = django_filters.CharFilter(field_name='request_path', lookup_expr='icontains')  # icontains表示该字段模糊搜索
#     # 模糊搜索
#     request_ip = django_filters.CharFilter(field_name='request_ip', lookup_expr='icontains')  # icontains表示该字段模糊搜索
#     request_os = django_filters.CharFilter(field_name='request_os', lookup_expr='icontains')  # icontains表示该字段模糊搜索
#     request_body = django_filters.CharFilter(field_name='request_body', lookup_expr='icontains')  # icontains表示该字段模糊搜索
#     request_method = django_filters.CharFilter(field_name='request_method', lookup_expr='icontains')
#
#     class Meta:
#         model = OperationLog
#         fields = ['start_time', 'end_time', 'request_modular', 'request_path', 'request_ip', 'request_os',
#                   'request_body', 'request_method']


class UsersManageTimeFilter(django_filters.rest_framework.FilterSet):
    """
    用户管理 简单过滤器
    URL格式：http://127.0.0.1:8000/?start_time=2020-12-02 12:00:00&end_time=2021-12-13 12:00:00
    field_name: 过滤字段名，一般应该对应模型中字段名
    lookup_expr: 查询时所要进行的操作，和ORM中运算符一致
    fields：指明过滤字段，可以是列表，列表中字典可以过滤，默认是判等；也可以字典，字典可以自定义操作
    exclude = ['password'] 排除字段，不允许使用列表中字典进行过滤
    自定义字段名可以和模型中不一致，但一定要用参数field_name指明对应模型中的字段名
    """
    #开始时间
    start_time = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='gte')  # 指定过滤的字段
    #结束时间
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
        fields = ['end_time', 'end_time','username','mobile','is_active','nickname','name']
