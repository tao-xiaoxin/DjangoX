# -*- coding: utf-8 -*-
from collections import OrderedDict

from django.core import paginator
from django.core.paginator import Paginator as DjangoPaginator
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.core.paginator import InvalidPage
from django.utils.translation import gettext_lazy as _


class CustomPagination(PageNumberPagination):
    """
    全局的分页类，所有的list请求会调用
    """
    page_size = 10  # 默认每页显示的数量
    page_size_query_param = "limit"  # 前端发送的页数关键字名
    page_query_param = "page"  # 前端发送的页码关键字名
    max_page_size = 999
    django_paginator_class = DjangoPaginator
    invalid_page_message = _('无效的页码,当前页数已超过最大值!')

    def paginate_queryset(self, queryset, request, view=None):
        """
        重写paginate_queryset让分页超过正常分页:有原来的4000错误无效页面。改写为返回200成功，data=[]提示
        """
        page_size = self.get_page_size(request)
        if not page_size:
            return None
        paginator = self.django_paginator_class(queryset, page_size)
        page_number = self.get_page_number(request, paginator)
        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            self.page = []

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request
        return list(self.page)

    def get_paginated_response(self, data):
        """
        重写get_paginated_response方法，返回自定义的分页格式
        """
        code = 200
        msg = 'success'
        current_page = int(self.get_page_number(self.request, paginator)) or 1
        limit = int(self.get_page_size(self.request)) or 10
        total = self.page.paginator.count if self.page else 0
        res = {
            "page": current_page,
            "total": total,
            "limit": limit,
            "data": data
        }
        if not data:
            code = 200
            msg = "暂无数据"
            res['data'] = []

        return Response(OrderedDict([
            ('code', code),
            ('msg', msg),
            ('data', res),
        ]))
