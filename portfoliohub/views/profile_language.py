from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from life_hub.renderers import UserRenderer

from portfoliohub.models.profile_snapshot import ProfileSnapshot
from portfoliohub.models.profile_language import ProfileLanguage

from portfoliohub.serializers.profile_language import (
    ProfileLanguageSerializer
)


# ============================================
# LIST + CREATE
# ============================================

class ProfileLanguageAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request, snapshot_id):

        snapshot = get_object_or_404(
            ProfileSnapshot,
            profile_snapshot_id=snapshot_id,
            user=request.user
        )

        languages = ProfileLanguage.objects.filter(
            profile_snapshot=snapshot
        ).select_related("language")

        serializer = ProfileLanguageSerializer(
            languages,
            many=True
        )

        return Response({
            "message": "Languages fetched successfully",
            "data": serializer.data
        })

    def post(self, request, snapshot_id):

        data = request.data.copy()
        data["profile_snapshot_id"] = snapshot_id

        serializer = ProfileLanguageSerializer(
            data=data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Language added successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


# ============================================
# UPDATE + DELETE
# ============================================

class ProfileLanguageDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get_object(self, request, language_mapping_id):

        return get_object_or_404(
            ProfileLanguage,
            profilelanguage_id=language_mapping_id,
            profile_snapshot__user=request.user
        )

    def put(self, request, language_mapping_id):

        mapping = self.get_object(
            request,
            language_mapping_id
        )

        serializer = ProfileLanguageSerializer(
            mapping,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Language updated successfully",
            "data": serializer.data
        })

    def delete(self, request, language_mapping_id):

        mapping = self.get_object(
            request,
            language_mapping_id
        )

        mapping.delete()

        return Response({
            "message": "Language removed successfully"
        })


# ============================================
# REORDER
# ============================================

class ProfileLanguageReorderAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def post(self, request, snapshot_id):

        snapshot = get_object_or_404(
            ProfileSnapshot,
            profile_snapshot_id=snapshot_id,
            user=request.user
        )

        order = request.data.get("order", [])

        for index, language_id in enumerate(order):

            ProfileLanguage.objects.filter(
                profilelanguage_id=language_id,
                profile_snapshot=snapshot
            ).update(position=index)

        return Response({
            "message": "Languages reordered successfully"
        })
