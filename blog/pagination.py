# blog/pagination.py
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.response import Response
from collections import OrderedDict

class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('status', 'success'),
            ('meta', OrderedDict([
                ('current_page', self.page.number),
                ('total_pages', self.page.paginator.num_pages),
                ('total_count', self.page.paginator.count),
                ('page_size', self.get_page_size(self.request)),
                ('has_next', self.page.has_next()),
                ('has_previous', self.page.has_previous()),
            ])),
            ('data', data)
        ]))

class CustomLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 10
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    max_limit = 100

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('status', 'success'),
            ('meta', OrderedDict([
                ('limit', self.get_limit(self.request)),
                ('offset', self.get_offset(self.request)),
                ('total_count', self.count),
                ('next_link', self.get_next_link()),
                ('previous_link', self.get_previous_link()),
            ])),
            ('data', data)
        ]))