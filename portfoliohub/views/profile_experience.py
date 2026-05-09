from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404

from life_hub.renderers import UserRenderer
from portfoliohub.models.profile_experience import ProfileExperience
from portfoliohub.models.profile_snapshot import ProfileSnapshot
from portfoliohub.serializers.profile_experience import ProfileExperienceSerializer


# ============================================
# LIST + CREATE
# ============================================

class ProfileExperienceAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request, snapshot_id):
        snapshot = get_object_or_404(
            ProfileSnapshot,
            profile_snapshot_id=snapshot_id,
            user=request.user
        )

        experiences = ProfileExperience.objects.filter(
            profile_snapshot=snapshot
        ).order_by("-start_date", "position")

        serializer = ProfileExperienceSerializer(experiences, many=True)

        return Response({
            "message": "Experience list fetched successfully",
            "data": serializer.data
        })

    def post(self, request, snapshot_id):
        data = request.data.copy()
        data["profile_snapshot_id"] = snapshot_id

        serializer = ProfileExperienceSerializer(
            data=data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Experience added successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


# ============================================
# UPDATE + DELETE
# ============================================

class ProfileExperienceDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get_object(self, request, exp_id):
        return get_object_or_404(
            ProfileExperience,
            profileexperience_id=exp_id,
            profile_snapshot__user=request.user
        )

    def put(self, request, exp_id):
        exp = self.get_object(request, exp_id)

        serializer = ProfileExperienceSerializer(
            exp,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Experience updated successfully",
            "data": serializer.data
        })

    def delete(self, request, exp_id):
        exp = self.get_object(request, exp_id)
        exp.delete()

        return Response({
            "message": "Experience deleted successfully"
        })


# ============================================
# REORDER
# ============================================

class ProfileExperienceReorderAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def post(self, request, snapshot_id):
        snapshot = get_object_or_404(
            ProfileSnapshot,
            profile_snapshot_id=snapshot_id,
            user=request.user
        )

        order = request.data.get("order", [])

        for index, exp_id in enumerate(order):
            ProfileExperience.objects.filter(
                profileexperience_id=exp_id,
                profile_snapshot=snapshot
            ).update(position=index)

        return Response({
            "message": "Experience reordered successfully"
        })
