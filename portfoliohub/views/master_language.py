from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404

from life_hub.renderers import UserRenderer

from portfoliohub.models.master_language import MasterLanguage
from portfoliohub.serializers.master_language import (
    MasterLanguageSerializer
)


# ============================================
# LIST + CREATE
# ============================================

class MasterLanguageAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request):

        languages = MasterLanguage.objects.filter(
            is_active=True
        ).order_by("position", "name")

        serializer = MasterLanguageSerializer(
            languages,
            many=True
        )

        return Response({
            "message": "Languages fetched successfully",
            "data": serializer.data
        })

    def post(self, request):

        # OPTIONAL:
        # You can later add IsAdminUser permission

        serializer = MasterLanguageSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Language created successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


# ============================================
# DETAIL + UPDATE + DELETE
# ============================================

class MasterLanguageDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get_object(self, language_id):

        return get_object_or_404(
            MasterLanguage,
            masterlanguage_id=language_id
        )

    def get(self, request, language_id):

        language = self.get_object(language_id)

        serializer = MasterLanguageSerializer(language)

        return Response({
            "message": "Language fetched successfully",
            "data": serializer.data
        })

    def put(self, request, language_id):

        language = self.get_object(language_id)

        serializer = MasterLanguageSerializer(
            language,
            data=request.data,
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Language updated successfully",
            "data": serializer.data
        })

    def delete(self, request, language_id):

        language = self.get_object(language_id)

        language.delete()

        return Response({
            "message": "Language deleted successfully"
        })
