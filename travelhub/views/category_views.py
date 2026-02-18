# travelhub/views/category_views.py

from django.utils import timezone
from django.db.models import Count, Q

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from travelhub.models import SpotCategory
from travelhub.serializers import SpotCategorySerializer
from life_hub.renderers import UserRenderer

from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from travelhub.pagination import SpotCategoryOffsetPagination

# ======================================================
# PUBLIC LISTING (ONE ROUTE, PUBLIC ONLY)
# ======================================================


class SpotCategoryListAPIView(APIView):
    """
    Public listing:
    - Anyone can access
    - Only active SpotCategory
    """
    renderer_classes = [UserRenderer]
    permission_classes = []

    def get(self, request):
        categories = SpotCategory.objects.filter(
            is_active=True,
            deleted_at__isnull=True
        ).annotate(
            total_spots=Count(
                "travel_spots",
                filter=Q(travel_spots__is_active=True),
                distinct=True
            )
        ).order_by("name")

        serializer = SpotCategorySerializer(categories, many=True)

        return Response({
            "message": "Spot Categories fetched successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


# ======================================================
# FULL VIEW (SAME ROUTE FOR PUBLIC + ADMIN)
# ======================================================

class SpotCategoryDetailAPIView(APIView):
    """
    Full view:
    - Public → limited data (only if active)
    - Authenticated → full data
    """
    renderer_classes = [UserRenderer]
    permission_classes = []

    def get_object(self, slug):
        try:
            return SpotCategory.objects.get(
                slug=slug,
                deleted_at__isnull=True
            )
        except SpotCategory.DoesNotExist:
            return None

    def get(self, request, slug):
        category = self.get_object(slug)

        if not category:
            return Response(
                {"message": "Spot Category not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = SpotCategorySerializer(category)

        return Response({
            "message": f"Spot Category '{category.name}' has been fetched successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


# ======================================================
# ADMIN CRUD (SAME DETAIL ROUTE, WRITE REQUIRES AUTH)
# ======================================================

class SpotCategoryListCreateAPIView(APIView):
    """
    Admin listing + create
    """
    renderer_classes = [UserRenderer]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        queryset = SpotCategory.objects.filter(
            deleted_at__isnull=True
        ).annotate(
            total_spots=Count(
                "travel_spots",
                filter=Q(travel_spots__is_active=True),
                distinct=True
            )
        )

        # -------------------------
        # Filters
        # -------------------------
        search = request.query_params.get("search")
        is_active = request.query_params.get("is_active")

        if is_active in ["true", "false"]:
            queryset = queryset.filter(is_active=(is_active == "true"))

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
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
        ]

        ordering = request.query_params.get("ordering", "-created_at")

        if ordering not in allowed_orderings:
            ordering = "-created_at"

        # APPLY ORDERING HERE (important)
        queryset = queryset.order_by(ordering)

        # -------------------------
        # Offset Pagination
        # -------------------------

        paginator = SpotCategoryOffsetPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)

        serializer = SpotCategorySerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = SpotCategorySerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            instance = serializer.save()
            return Response({
                "message": f"Spot Category '{instance.name}' created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SpotCategoryUpdateDeleteAPIView(APIView):
    """
    Admin update & delete
    """
    renderer_classes = [UserRenderer]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, slug):
        try:
            return SpotCategory.objects.get(
                slug=slug,
                deleted_at__isnull=True
            )
        except SpotCategory.DoesNotExist:
            return None

    def put(self, request, slug):
        category = self.get_object(slug)
        if not category:
            return Response(
                {"message": "Spot Category not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = SpotCategorySerializer(
            category,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": f"Spot Category '{category.name}' has been updated successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug):
        category = self.get_object(slug)
        if not category:
            return Response(
                {"message": "Spot Category not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Soft delete
        category.is_active = False
        category.deleted_at = timezone.now()
        category.save()

        return Response(
            {"message": f"Spot Category '{category.name}' has been deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )


class SpotCategoryCheckAPIView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        name = request.query_params.get("name", "").strip()
        exclude_id = request.query_params.get("exclude_id")

        if not name:
            return Response({
                "message": "Name is empty",
                "data": {
                    "exists": False
                }
            })

        query = SpotCategory.objects.filter(
            name__iexact=name,
            deleted_at__isnull=True
        )

        # Skip current record in edit mode
        if exclude_id:
            query = query.exclude(spotcategory_id=exclude_id)

        exists = query.exists()

        return Response({
            "message": "Name check completed",
            "data": {
                "exists": exists
            }
        })
