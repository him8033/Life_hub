# travelhub/views/travelspot/details.py

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from life_hub.renderers import UserRenderer
from travelhub.models import TravelSpot
from travelhub.serializers.travelspot.details import (
    TravelSpotDetailsSerializer
)


class TravelSpotDetailsAPIView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def put(self, request, travelspot_id):
        spot = TravelSpot.objects.get(
            travelspot_id=travelspot_id,
            deleted_at__isnull=True
        )

        # if spot.completion_status != "location":
        #     return Response({"error": "Invalid step order"}, status=400)

        serializer = TravelSpotDetailsSerializer(
            spot,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        
        new_status = spot.completion_status
        if spot.completion_status == "location":
            new_status = "details"

        serializer.save(
            updated_by=request.user,
            completion_status=new_status
        )

        return Response(
            {
                "message": "Details step saved successfully!",
                "data": {
                    "travelspot_id": spot.travelspot_id,
                    "current_step": spot.completion_status,
                    "next_step": "images",
                }
            }
        )
        # return Response({"next_step": "images"})
