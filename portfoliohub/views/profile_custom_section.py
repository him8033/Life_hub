from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from life_hub.renderers import UserRenderer

from portfoliohub.models.profile_snapshot import ProfileSnapshot
from portfoliohub.models.profile_custom_section import (
    ProfileCustomSection
)

from portfoliohub.serializers.profile_custom_section import (
    ProfileCustomSectionSerializer
)


# ============================================
# LIST + CREATE
# ============================================

class ProfileCustomSectionAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request, snapshot_id):

        snapshot = get_object_or_404(
            ProfileSnapshot,
            profile_snapshot_id=snapshot_id,
            user=request.user
        )

        sections = ProfileCustomSection.objects.filter(
            profile_snapshot=snapshot
        ).order_by("position")

        serializer = ProfileCustomSectionSerializer(
            sections,
            many=True
        )

        return Response({
            "message": "Custom sections fetched successfully",
            "data": serializer.data
        })

    def post(self, request, snapshot_id):

        data = request.data.copy()
        data["profile_snapshot_id"] = snapshot_id

        serializer = ProfileCustomSectionSerializer(
            data=data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Custom section added successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


# ============================================
# UPDATE + DELETE
# ============================================

class ProfileCustomSectionDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get_object(self, request, section_id):

        return get_object_or_404(
            ProfileCustomSection,
            profilecustomsection_id=section_id,
            profile_snapshot__user=request.user
        )

    # ============================================
    # UPDATE
    # ============================================

    def put(self, request, section_id):

        section = self.get_object(request, section_id)

        serializer = ProfileCustomSectionSerializer(
            section,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Custom section updated successfully",
            "data": serializer.data
        })

    # ============================================
    # DELETE
    # ============================================

    def delete(self, request, section_id):

        section = self.get_object(request, section_id)

        section.delete()

        return Response({
            "message": "Custom section deleted successfully"
        })


# ============================================
# REORDER
# ============================================

class ProfileCustomSectionReorderAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def post(self, request, snapshot_id):

        snapshot = get_object_or_404(
            ProfileSnapshot,
            profile_snapshot_id=snapshot_id,
            user=request.user
        )

        order = request.data.get("order", [])

        for index, section_id in enumerate(order):

            ProfileCustomSection.objects.filter(
                profilecustomsection_id=section_id,
                profile_snapshot=snapshot
            ).update(position=index)

        return Response({
            "message": "Custom sections reordered successfully"
        })
