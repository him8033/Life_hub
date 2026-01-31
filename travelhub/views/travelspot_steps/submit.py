# travelhub/views/travelspot/basic_info.py

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from life_hub.renderers import UserRenderer
from travelhub.models import TravelSpot


class TravelSpotSubmitAPIView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request, travelspot_id):
        spot = TravelSpot.objects.get(
            travelspot_id=travelspot_id,
            deleted_at__isnull=True
        )

        # if spot.completion_status != "images":
        #     return Response({"error": "Complete all steps first"}, status=400)

        spot.is_ready_for_review = True
        spot.completion_status = "complete"
        spot.updated_by = request.user
        spot.save()

        return Response(
            {
                "message": "Submitted for review.",
                "data": {
                    "travelspot_id": spot.travelspot_id,
                    "current_step": spot.completion_status,
                    "next_step": "",
                }
            }
        )
        # return Response({"status": "Submitted for review"})
