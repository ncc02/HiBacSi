import rest_framework.pagination as pagination
from rest_framework.response import Response

class CustomPageNumberPagination(pagination.PageNumberPagination):
    page_size = 1
    page_size_query_param = 'count'
    max_page_size = 5
    page_query_param = 'p'

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'results': data
        })
    
class CustomLimitOffsetPagination(pagination.LimitOffsetPagination):
    default_limit = 10
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    max_limit = 100

    def get_paginated_response(self, data):
        return Response({
            # 'links': {
            #     'next': self.get_next_link(),
            #     'previous': self.get_previous_link()
            # },
            'total_page': (self.count//self.limit + 1),
            'current_page': (self.offset//self.limit + 1),
            'count': self.count,
            'results': data
        })