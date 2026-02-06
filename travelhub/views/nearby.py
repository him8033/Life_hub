from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import F, FloatField, ExpressionWrapper
from django.db.models.functions import ACos, Cos, Sin, Radians
from travelhub.models import TravelSpot
from travelhub.serializers.nearby_spot import NearbySpotSerializer


class NearbyTravelSpotsAPIView(APIView):
    def get(self, request, slug):
        try:
            spot = TravelSpot.objects.get(
                slug=slug,
                is_active=True,
                deleted_at__isnull=True
            )
        except TravelSpot.DoesNotExist:
            return Response(
                {"message": "Travel spot not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if not spot.latitude or not spot.longitude:
            return Response(
                {"message": "Location not available for this spot"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get query params
        radius = float(request.query_params.get("radius", 50))
        limit = int(request.query_params.get("limit", 10))

        lat = float(spot.latitude)
        lon = float(spot.longitude)

        # Haversine formula
        distance_expr = ExpressionWrapper(
            6371 * ACos(
                Cos(Radians(lat)) *
                Cos(Radians(F("latitude"))) *
                Cos(Radians(F("longitude")) - Radians(lon)) +
                Sin(Radians(lat)) *
                Sin(Radians(F("latitude")))
            ),
            output_field=FloatField()
        )

        nearby_spots = (
            TravelSpot.objects
            .filter(
                is_active=True,
                deleted_at__isnull=True,
                latitude__isnull=False,
                longitude__isnull=False
            )
            .exclude(id=spot.id)
            .annotate(distance_km=distance_expr)
            .filter(distance_km__lte=radius)
            .order_by("distance_km")[:limit]
        )

        serializer = NearbySpotSerializer(nearby_spots, many=True)

        return Response({
            "message": "Nearby spots fetched successfully",
            "data": serializer.data
        })
