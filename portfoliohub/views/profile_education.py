from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404

from life_hub.renderers import UserRenderer
from portfoliohub.models.profile_education import ProfileEducation
from portfoliohub.models.profile_snapshot import ProfileSnapshot
from portfoliohub.serializers.profile_education import ProfileEducationSerializer


# ============================================
# LIST + CREATE
# ============================================

class ProfileEducationAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request, snapshot_id):
        snapshot = get_object_or_404(
            ProfileSnapshot,
            profile_snapshot_id=snapshot_id,
            user=request.user
        )

        educations = ProfileEducation.objects.filter(
            profile_snapshot=snapshot
        ).order_by("-start_date", "position")

        serializer = ProfileEducationSerializer(educations, many=True)

        return Response({
            "message": "Education list fetched successfully",
            "data": serializer.data
        })

    def post(self, request, snapshot_id):
        data = request.data.copy()
        data["profile_snapshot_id"] = snapshot_id

        serializer = ProfileEducationSerializer(
            data=data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Education added successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


# ============================================
# UPDATE + DELETE
# ============================================

class ProfileEducationDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get_object(self, request, edu_id):
        return get_object_or_404(
            ProfileEducation,
            profileeducation_id=edu_id,
            profile_snapshot__user=request.user
        )

    def put(self, request, edu_id):
        education = self.get_object(request, edu_id)

        serializer = ProfileEducationSerializer(
            education,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Education updated successfully",
            "data": serializer.data
        })

    def delete(self, request, edu_id):
        education = self.get_object(request, edu_id)
        education.delete()

        return Response({
            "message": "Education deleted successfully"
        }, status=status.HTTP_200_OK)


# ============================================
# REORDER (OPTIONAL BUT IMPORTANT)
# ============================================

class ProfileEducationReorderAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def post(self, request, snapshot_id):
        snapshot = get_object_or_404(
            ProfileSnapshot,
            profile_snapshot_id=snapshot_id,
            user=request.user
        )

        order = request.data.get("order", [])

        for index, edu_id in enumerate(order):
            ProfileEducation.objects.filter(
                profileeducation_id=edu_id,
                profile_snapshot=snapshot
            ).update(position=index)

        return Response({
            "message": "Education reordered successfully"
        })
