from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .models import TravelSpot
from .serializers import (
    TravelSpotSerializer
)
from .renderers import UserRenderer


# ======================================================
# 🌍 PUBLIC LISTING (ONE ROUTE, PUBLIC ONLY)
# ======================================================

class TravelSpotListAPIView(APIView):
    """
    Public listing:
    - Anyone can access
    - Only active travel spots
    - Limited fields (Public serializer)
    """
    renderer_classes = [UserRenderer]
    permission_classes = []

    def get(self, request):
        spots = TravelSpot.objects.filter(
            is_active=True,
            deleted_at__isnull=True
        ).order_by("-created_at")

        serializer = TravelSpotSerializer(spots, many=True)

        return Response({
            "message": "Travel spots fetched successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


# ======================================================
# 🔍 FULL VIEW (SAME ROUTE FOR PUBLIC + ADMIN)
# ======================================================

class TravelSpotDetailAPIView(APIView):
    """
    Full view:
    - Public → limited data (only if active)
    - Authenticated → full data
    """
    renderer_classes = [UserRenderer]
    permission_classes = []

    def get_object(self, slug):
        try:
            return TravelSpot.objects.get(
                slug=slug,
                deleted_at__isnull=True
            )
        except TravelSpot.DoesNotExist:
            return None

    def get(self, request, slug):
        spot = self.get_object(slug)

        if not spot:
            return Response(
                {"message": "Travel spot not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # 🔐 Decide serializer based on auth
        # if request.user.is_authenticated:
        #     serializer = TravelSpotSerializer(spot)
        # else:
        #     if not spot.is_active:
        #         return Response(
        #             {"message": "Travel spot not available"},
        #             status=status.HTTP_404_NOT_FOUND
        #         )
        #     serializer = PublicTravelSpotSerializer(spot)
        serializer = TravelSpotSerializer(spot)

        return Response({
            "message": "Travel spot fetched successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


# ======================================================
# 🔐 ADMIN CRUD (SAME DETAIL ROUTE, WRITE REQUIRES AUTH)
# ======================================================

class TravelSpotListCreateAPIView(APIView):
    """
    Admin listing + create
    """
    renderer_classes = [UserRenderer]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        spots = TravelSpot.objects.filter(
            deleted_at__isnull=True
        ).order_by("-created_at")

        serializer = TravelSpotSerializer(spots, many=True)

        return Response({
            "message": "Travel spots fetched successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = TravelSpotSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Travel spot created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TravelSpotUpdateDeleteAPIView(APIView):
    """
    Admin update & delete
    """
    renderer_classes = [UserRenderer]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, slug):
        try:
            return TravelSpot.objects.get(
                slug=slug,
                deleted_at__isnull=True
            )
        except TravelSpot.DoesNotExist:
            return None

    def put(self, request, slug):
        spot = self.get_object(slug)
        if not spot:
            return Response(
                {"message": "Travel spot not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = TravelSpotSerializer(
            spot,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Travel spot updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug):
        spot = self.get_object(slug)
        if not spot:
            return Response(
                {"message": "Travel spot not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Soft delete
        spot.is_active = False
        spot.deleted_at = timezone.now()
        spot.save()

        return Response(
            {"message": "Travel spot deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )
