from django.utils import timezone
from django.db import models
from django.db.models import F
from datetime import timedelta

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from travelhub.models import TravelSpot
from travelhub.models.travelspot_view import TravelSpotView
from travelhub.serializers import TravelSpotSerializer
from travelhub.serializers.travelspot_view import TravelSpotViewSerializer
from life_hub.utils import get_client_ip
from life_hub.renderers import UserRenderer

# ======================================================
# FULL VIEW (SAME ROUTE FOR PUBLIC + ADMIN)
# ======================================================


class TravelSpotDetailAPIView(APIView):
    """
    Full view:
    - Public → limited data (only if active)
    - Authenticated → full data
    """
    renderer_classes = [UserRenderer]
    permission_classes = []

    def get_object(self, request, slug):
        try:
            if request.user.is_authenticated:
                return TravelSpot.objects.get(
                    slug=slug,
                    deleted_at__isnull=True
                )
            else:
                return TravelSpot.objects.get(
                    slug=slug,
                    is_active=True,
                    deleted_at__isnull=True
                )
        except TravelSpot.DoesNotExist:
            return None

    def get(self, request, slug):
        spot = self.get_object(request, slug)

        if not spot:
            return Response(
                {"message": "Travel spot not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # ===============================
        # View counting logic
        # ===============================
        ip = get_client_ip(request)
        user = request.user if request.user.is_authenticated else None
        since = timezone.now() - timedelta(hours=24)

        view_query = TravelSpotView.objects.filter(
            travelspot=spot,
            viewed_at__gte=since
        )

        if user:
            view_query = view_query.filter(
                models.Q(user=user) | models.Q(ip_address=ip)
            )
        else:
            view_query = view_query.filter(ip_address=ip)

        view_exists = view_query.exists()

        if not view_exists:
            TravelSpotView.objects.create(
                travelspot=spot,
                user=user,
                ip_address=ip
            )

            # Safe increment
            TravelSpot.objects.filter(pk=spot.pk).update(
                view_count=F("view_count") + 1
            )

            spot.refresh_from_db(fields=["view_count"])

        serializer = TravelSpotSerializer(spot)

        return Response({
            "message": "Travel spot fetched successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class TravelSpotUpdateDeleteAPIView(APIView):
    """
    Admin update & delete
    """
    renderer_classes = [UserRenderer]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, travelspot_id):
        try:
            return TravelSpot.objects.get(
                travelspot_id=travelspot_id,
                deleted_at__isnull=True
            )
        except TravelSpot.DoesNotExist:
            return None

    def put(self, request, travelspot_id):
        spot = self.get_object(travelspot_id)
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

    def delete(self, request, travelspot_id):
        spot = self.get_object(travelspot_id)
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


class TravelSpotNameCheckAPIView(APIView):
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

        query = TravelSpot.objects.filter(
            name__iexact=name,
            deleted_at__isnull=True
        )

        # Skip current record in edit mode
        if exclude_id:
            query = query.exclude(travelspot_id=exclude_id)

        exists = query.exists()

        return Response({
            "message": "Name check completed",
            "data": {
                "exists": exists
            }
        })


class TravelSpotVisitorListAPIView(APIView):
    """
    Admin: Get all visitors of a travel spot
    """
    renderer_classes = [UserRenderer]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, travelspot_id):
        spot = TravelSpot.objects.filter(
            travelspot_id=travelspot_id,
            deleted_at__isnull=True
        ).first()

        if not spot:
            return Response(
                {"message": "Travel spot not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        views = TravelSpotView.objects.filter(
            travelspot=spot
        ).order_by("-viewed_at")

        serializer = TravelSpotViewSerializer(views, many=True)

        return Response({
            "message": "Visitor list fetched successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
