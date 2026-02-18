from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import F, FloatField, ExpressionWrapper
from django.db.models.functions import ACos, Cos, Sin, Radians
from travelhub.models import TravelSpot
from travelhub.serializers.nearby_spot import NearbySpotSerializer
from travelhub.pagination import NearBySpotCursorPagination
from life_hub.renderers import UserRenderer


class NearbyTravelSpotsAPIView(APIView):
    renderer_classes = [UserRenderer]

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

        # query param
        try:
            radius = float(request.query_params.get("radius", 50))
        except (TypeError, ValueError):
            radius = 50

        sort = request.query_params.get("sort", "distance")
        if sort not in ["distance", "most_visited"]:
            sort = "distance"

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

        queryset = (
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
        )

        # -------------------------
        # Offset Pagination
        # -------------------------

        paginator = NearBySpotCursorPagination()
                
        # Set ordering dynamically
        if sort == "most_visited":
            paginator.ordering = ("-view_count", "distance_km", "id")
        else:
            paginator.ordering = ("distance_km", "id")
            
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = NearbySpotSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)
