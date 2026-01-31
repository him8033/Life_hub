# travelhub/views/travelspot_steps/basic_info.py

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from life_hub.renderers import UserRenderer
from travelhub.models import TravelSpot
from travelhub.serializers.travelspot.basic_info import (
    TravelSpotBasicInfoSerializer
)


class TravelSpotBasicInfoAPIView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TravelSpotBasicInfoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        spot = serializer.save(
            created_by=request.user,
            updated_by=request.user,
            completion_status="basic_info"
        )

        return Response(
            {
                "message": "Basic information created successfully!",
                "data": {
                    "travelspot_id": spot.travelspot_id,
                    "basic_info": serializer.data,
                    "next_step": "location"
                }
            },
            status=status.HTTP_201_CREATED
        )

    # UPDATE
    def put(self, request, travelspot_id):
        spot = TravelSpot.objects.get(
            travelspot_id=travelspot_id,
            deleted_at__isnull=True
        )

        # Do not allow edit after submit
        # if spot.completion_status == "complete":
        #     return Response(
        #         {"message": "Cannot edit after submission"},
        #         status=status.HTTP_400_BAD_REQUEST
        #     )

        serializer = TravelSpotBasicInfoSerializer(
            spot,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)

        serializer.save(
            updated_by=request.user
        )

        return Response(
            {
                "message": "Basic information updated successfully!",
                "data": {
                    "travelspot_id": spot.travelspot_id,
                    "current_step": spot.completion_status,
                    "next_step": "location",
                }
            }
        )
