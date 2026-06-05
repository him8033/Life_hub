from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import (
    MultiPartParser,
    FormParser
)
from rest_framework import status
import cloudinary.uploader

from life_hub.renderers import UserRenderer

from portfoliohub.models.profile_snapshot import ProfileSnapshot
from portfoliohub.models.profile_project import ProfileProject

from portfoliohub.serializers.profile_project import (
    ProfileProjectSerializer
)


# ============================================
# LIST + CREATE
# ============================================

class ProfileProjectAPIView(APIView):
    renderer_classes = [UserRenderer]

    permission_classes = [IsAuthenticated]

    parser_classes = [
        MultiPartParser,
        FormParser
    ]

    def get(self, request, snapshot_id):

        snapshot = get_object_or_404(
            ProfileSnapshot,
            profile_snapshot_id=snapshot_id,
            user=request.user
        )

        queryset = ProfileProject.objects.filter(
            profile_snapshot=snapshot
        ).order_by(
            "position",
            "priority"
        )

        serializer = ProfileProjectSerializer(
            queryset,
            many=True
        )

        return Response({
            "message": "Projects fetched successfully",
            "data": serializer.data
        })

    def post(self, request, snapshot_id):

        data = request.data.copy()

        data["profile_snapshot_id"] = snapshot_id

        serializer = ProfileProjectSerializer(
            data=data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response({
            "message": "Project created successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


# ============================================
# UPDATE + DELETE
# ============================================

class ProfileProjectDetailAPIView(APIView):
    renderer_classes = [UserRenderer]

    permission_classes = [IsAuthenticated]

    parser_classes = [
        MultiPartParser,
        FormParser
    ]

    def get_object(self, request, project_id):

        return get_object_or_404(
            ProfileProject,
            profileproject_id=project_id,
            profile_snapshot__user=request.user
        )

    def get(self, request, project_id):

        project = self.get_object(
            request,
            project_id
        )

        serializer = ProfileProjectSerializer(
            project
        )

        return Response({
            "message": "Project fetched successfully",
            "data": serializer.data
        })

    def put(self, request, project_id):

        project = self.get_object(
            request,
            project_id
        )

        serializer = ProfileProjectSerializer(
            project,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response({
            "message": "Project updated successfully",
            "data": serializer.data
        })

    def delete(self, request, project_id):

        project = self.get_object(
            request,
            project_id
        )

        # DELETE CLOUDINARY IMAGE
        if project.public_id:
            cloudinary.uploader.destroy(
                project.public_id
            )

        project.delete()

        return Response({
            "message": "Project deleted successfully"
        })


# ============================================
# PROJECT REORDER
# ============================================


class ProfileProjectReorderAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def post(self, request, snapshot_id):

        snapshot = get_object_or_404(
            ProfileSnapshot,
            profile_snapshot_id=snapshot_id,
            user=request.user
        )

        order = request.data.get("order", [])

        for index, project_id in enumerate(order):

            ProfileProject.objects.filter(
                profileproject_id=project_id,
                profile_snapshot=snapshot
            ).update(position=index)

        return Response({
            "message": "Projects reordered successfully"
        })
