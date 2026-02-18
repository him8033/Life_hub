from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Q

from travelhub.models import TravelSpot
from travelhub.serializers import TravelSpotSerializer
from travelhub.pagination import TravelSpotCursorPagination
from travelhub.pagination import TravelSpotOffsetPagination
from life_hub.renderers import UserRenderer


class TravelSpotListAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [UserRenderer]

    def get(self, request):
        queryset = TravelSpot.objects.filter(is_active=True)

        # -------------------------
        # Filters
        # -------------------------
        state = request.query_params.get("state")
        district = request.query_params.get("district")
        sub_district = request.query_params.get("sub_district")
        village = request.query_params.get("village")
        category = request.query_params.get("category")
        min_views = request.query_params.get("min_views")
        search = request.query_params.get("search")

        if state:
            queryset = queryset.filter(state_id=state)

        if district:
            queryset = queryset.filter(district_id=district)

        if sub_district:
            queryset = queryset.filter(sub_district_id=sub_district)

        if village:
            queryset = queryset.filter(village_id=village)

        if category:
            queryset = queryset.filter(categories__id=category)

        if min_views:
            queryset = queryset.filter(view_count__gte=min_views)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(short_description__icontains=search) |
                Q(long_description__icontains=search) |
                Q(full_address__icontains=search)
            )

        # Avoid duplicates due to M2M
        queryset = queryset.distinct()

        # -------------------------
        # Sorting
        # -------------------------
        allowed_orderings = [
            "name",
            "-name",
            "created_at",
            "-created_at",
            "view_count",
            "-view_count",
        ]

        ordering = request.query_params.get("ordering", "-created_at")

        if ordering not in allowed_orderings:
            ordering = "-created_at"

        # -------------------------
        # Cursor Pagination
        # -------------------------
        paginator = TravelSpotCursorPagination()

        # IMPORTANT: override paginator ordering
        paginator.ordering = ordering

        page = paginator.paginate_queryset(queryset, request, view=self)

        serializer = TravelSpotSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)


class TravelSpotListCreateAPIView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        queryset = TravelSpot.objects.filter(deleted_at__isnull=True)

        # -------------------------
        # Filters
        # -------------------------
        state = request.query_params.get("state")
        district = request.query_params.get("district")
        sub_district = request.query_params.get("sub_district")
        village = request.query_params.get("village")
        category = request.query_params.get("category")
        min_views = request.query_params.get("min_views")
        search = request.query_params.get("search")
        is_active = request.query_params.get("is_active")

        if state:
            queryset = queryset.filter(state_id=state)

        if district:
            queryset = queryset.filter(district_id=district)

        if sub_district:
            queryset = queryset.filter(sub_district_id=sub_district)

        if village:
            queryset = queryset.filter(village_id=village)

        if category:
            queryset = queryset.filter(categories__id=category)

        if min_views:
            queryset = queryset.filter(view_count__gte=min_views)

        if is_active in ["true", "false"]:
            queryset = queryset.filter(is_active=(is_active == "true"))

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(short_description__icontains=search) |
                Q(long_description__icontains=search) |
                Q(full_address__icontains=search)
            )

        # Avoid duplicates due to M2M
        queryset = queryset.distinct()

        # -------------------------
        # Sorting
        # -------------------------
        allowed_orderings = [
            "name",
            "-name",
            "created_at",
            "-created_at",
            "view_count",
            "-view_count",
        ]

        ordering = request.query_params.get("ordering", "-created_at")

        if ordering not in allowed_orderings:
            ordering = "-created_at"

        # APPLY ORDERING HERE (important)
        queryset = queryset.order_by(ordering)

        # -------------------------
        # Offset Pagination
        # -------------------------

        paginator = TravelSpotOffsetPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)

        serializer = TravelSpotSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
