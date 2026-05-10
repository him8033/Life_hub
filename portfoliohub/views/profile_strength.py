from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from life_hub.renderers import UserRenderer

from portfoliohub.models.profile_snapshot import ProfileSnapshot
from portfoliohub.models.profile_strength import ProfileStrength

from portfoliohub.serializers.profile_strength import (
    ProfileStrengthSerializer
)


# ============================================
# LIST + CREATE
# ============================================

class ProfileStrengthAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request, snapshot_id):

        snapshot = get_object_or_404(
            ProfileSnapshot,
            profile_snapshot_id=snapshot_id,
            user=request.user
        )

        strengths = ProfileStrength.objects.filter(
            profile_snapshot=snapshot
        ).order_by("position")

        serializer = ProfileStrengthSerializer(
            strengths,
            many=True
        )

        return Response({
            "message": "Strengths fetched successfully",
            "data": serializer.data
        })

    def post(self, request, snapshot_id):

        data = request.data.copy()
        data["profile_snapshot_id"] = snapshot_id

        serializer = ProfileStrengthSerializer(
            data=data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Strength added successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


# ============================================
# UPDATE + DELETE
# ============================================

class ProfileStrengthDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get_object(self, request, strength_id):
        return get_object_or_404(
            ProfileStrength,
            profilestrength_id=strength_id,
            profile_snapshot__user=request.user
        )

    # ============================================
    # UPDATE
    # ============================================

    def put(self, request, strength_id):

        strength = self.get_object(request, strength_id)

        serializer = ProfileStrengthSerializer(
            strength,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Strength updated successfully",
            "data": serializer.data
        })

    # ============================================
    # DELETE
    # ============================================

    def delete(self, request, strength_id):

        strength = self.get_object(request, strength_id)

        strength.delete()

        return Response({
            "message": "Strength deleted successfully"
        })


# ============================================
# REORDER
# ============================================

class ProfileStrengthReorderAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def post(self, request, snapshot_id):

        snapshot = get_object_or_404(
            ProfileSnapshot,
            profile_snapshot_id=snapshot_id,
            user=request.user
        )

        order = request.data.get("order", [])

        for index, strength_id in enumerate(order):

            ProfileStrength.objects.filter(
                profilestrength_id=strength_id,
                profile_snapshot=snapshot
            ).update(position=index)

        return Response({
            "message": "Strengths reordered successfully"
        })
