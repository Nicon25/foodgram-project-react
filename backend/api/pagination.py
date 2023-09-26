from rest_framework import pagination


class LimitPagination(pagination.PageNumberPagination):
    page_size_query_param = 'limit'
