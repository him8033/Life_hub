# portfoliohub/views/master_section.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from life_hub.renderers import UserRenderer

from portfoliohub.models.master_section import MasterSection
from portfoliohub.serializers.master_section import MasterSectionSerializer


class MasterSectionAPIView(APIView):

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request):

        sections = (
            MasterSection.objects
            .filter(is_active=True)
            .order_by("name")
        )

        serializer = MasterSectionSerializer(
            sections,
            many=True
        )

        return Response({
            "message": "Sections fetched successfully",
            "data": serializer.data
        })
