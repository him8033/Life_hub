# travelhub/views/category_views.py

from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from travelhub.models import SpotCategory
from travelhub.serializers import SpotCategorySerializer
from travelhub.renderers import UserRenderer

from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

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
        ).order_by("-created_at")

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
        category = SpotCategory.objects.filter(
            deleted_at__isnull=True
        ).order_by("-created_at")

        serializer = SpotCategorySerializer(category, many=True)

        return Response({
            "message": "Spot Categories fetched successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

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
