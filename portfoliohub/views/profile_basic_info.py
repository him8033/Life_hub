from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404

from life_hub.renderers import UserRenderer
from portfoliohub.models.profile_basic_info import ProfileBasicInfo
from portfoliohub.models.profile_snapshot import ProfileSnapshot
from portfoliohub.serializers.profile_basic_info import ProfileBasicInfoSerializer


# ============================================
# BASIC INFO CREATE / GET / UPDATE
# ============================================

class ProfileBasicInfoAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request, snapshot_id):
        snapshot = get_object_or_404(
            ProfileSnapshot,
            profile_snapshot_id=snapshot_id,
            user=request.user
        )

        basic_info = ProfileBasicInfo.objects.filter(
            profile_snapshot=snapshot
        ).first()

        if not basic_info:
            return Response({
                "message": "No basic info found",
                "data": None
            })

        serializer = ProfileBasicInfoSerializer(basic_info)

        return Response({
            "message": "Basic info fetched successfully",
            "data": serializer.data
        })

    def post(self, request, snapshot_id):
        data = request.data.copy()
        data["profile_snapshot_id"] = snapshot_id

        serializer = ProfileBasicInfoSerializer(
            data=data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Basic info saved successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)
