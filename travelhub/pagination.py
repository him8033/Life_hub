from rest_framework.pagination import CursorPagination
from rest_framework.pagination import PageNumberPagination


class TravelSpotCursorPagination(CursorPagination):
    page_size = 9
    ordering = "-created_at"   # required for cursor pagination
    cursor_query_param = "cursor"


class TravelSpotOffsetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class SpotCategoryOffsetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class NearBySpotCursorPagination(CursorPagination):
    page_size = 8
    ordering = "-created_at"   # required for cursor pagination
    cursor_query_param = "cursor"
