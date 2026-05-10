from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from life_hub.renderers import UserRenderer

from portfoliohub.models.profile_snapshot import ProfileSnapshot
from portfoliohub.models.profile_achievement import ProfileAchievement

from portfoliohub.serializers.profile_achievement import (
    ProfileAchievementSerializer
)


# ============================================
# LIST + CREATE
# ============================================

class ProfileAchievementAPIView(APIView):

    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request, snapshot_id):

        snapshot = get_object_or_404(
            ProfileSnapshot,
            profile_snapshot_id=snapshot_id,
            user=request.user
        )

        achievements = ProfileAchievement.objects.filter(
            profile_snapshot=snapshot
        ).order_by("position", "-created_at")

        serializer = ProfileAchievementSerializer(
            achievements,
            many=True
        )

        return Response({
            "message": "Achievements fetched successfully",
            "data": serializer.data
        })

    def post(self, request, snapshot_id):

        data = request.data.copy()

        data["profile_snapshot_id"] = snapshot_id

        serializer = ProfileAchievementSerializer(
            data=data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Achievement added successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


# ============================================
# UPDATE + DELETE
# ============================================

class ProfileAchievementDetailAPIView(APIView):

    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get_object(self, request, achievement_id):

        return get_object_or_404(
            ProfileAchievement,
            profileachievement_id=achievement_id,
            profile_snapshot__user=request.user
        )

    def put(self, request, achievement_id):

        achievement = self.get_object(
            request,
            achievement_id
        )

        serializer = ProfileAchievementSerializer(
            achievement,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Achievement updated successfully",
            "data": serializer.data
        })

    def delete(self, request, achievement_id):

        achievement = self.get_object(
            request,
            achievement_id
        )

        achievement.delete()

        return Response({
            "message": "Achievement deleted successfully"
        })


# ============================================
# REORDER
# ============================================

class ProfileAchievementReorderAPIView(APIView):

    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def post(self, request, snapshot_id):

        snapshot = get_object_or_404(
            ProfileSnapshot,
            profile_snapshot_id=snapshot_id,
            user=request.user
        )

        order = request.data.get("order", [])

        for index, achievement_id in enumerate(order):

            ProfileAchievement.objects.filter(
                profileachievement_id=achievement_id,
                profile_snapshot=snapshot
            ).update(position=index)

        return Response({
            "message": "Achievements reordered successfully"
        })
