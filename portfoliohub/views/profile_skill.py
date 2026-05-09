from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404

from life_hub.renderers import UserRenderer

from portfoliohub.models.profile_snapshot import ProfileSnapshot
from portfoliohub.models.profile_skill import ProfileSkill

from portfoliohub.serializers.profile_skill import (
    ProfileSkillSerializer
)


# ============================================
# LIST + CREATE
# ============================================

class ProfileSkillAPIView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request, snapshot_id):

        snapshot = get_object_or_404(
            ProfileSnapshot,
            profile_snapshot_id=snapshot_id,
            user=request.user
        )

        queryset = ProfileSkill.objects.filter(
            profile_snapshot=snapshot
        ).select_related(
            "skill",
            "skill__category"
        ).order_by(
            "position",
            "priority"
        )

        serializer = ProfileSkillSerializer(
            queryset,
            many=True
        )

        return Response({
            "message": "Profile skills fetched successfully",
            "data": serializer.data
        })

    def post(self, request, snapshot_id):

        data = request.data.copy()

        data["profile_snapshot_id"] = snapshot_id

        serializer = ProfileSkillSerializer(
            data=data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Skill added successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


# ============================================
# UPDATE + DELETE
# ============================================

class ProfileSkillDetailAPIView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get_object(self, request, skill_id):

        return get_object_or_404(
            ProfileSkill,
            profileskill_id=skill_id,
            profile_snapshot__user=request.user
        )

    def put(self, request, skill_id):

        profile_skill = self.get_object(
            request,
            skill_id
        )

        serializer = ProfileSkillSerializer(
            profile_skill,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Profile skill updated successfully",
            "data": serializer.data
        })

    def delete(self, request, skill_id):

        profile_skill = self.get_object(
            request,
            skill_id
        )

        profile_skill.delete()

        return Response({
            "message": "Profile skill removed successfully"
        })


# ============================================
# REORDER
# ============================================

class ProfileSkillReorderAPIView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request, snapshot_id):

        snapshot = get_object_or_404(
            ProfileSnapshot,
            profile_snapshot_id=snapshot_id,
            user=request.user
        )

        order = request.data.get("order", [])

        for index, skill_id in enumerate(order):

            ProfileSkill.objects.filter(
                profileskill_id=skill_id,
                profile_snapshot=snapshot
            ).update(position=index)

        return Response({
            "message": "Skills reordered successfully"
        })
