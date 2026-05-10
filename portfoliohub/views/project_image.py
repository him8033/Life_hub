from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from django.shortcuts import get_object_or_404

from life_hub.renderers import UserRenderer

from portfoliohub.models.project_image import ProjectImage
from portfoliohub.models.profile_project import ProfileProject

from portfoliohub.serializers.project_image import (
    ProjectImageSerializer
)

import cloudinary.uploader


# ============================================
# LIST + CREATE
# ============================================

class ProjectImageAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request, project_id):

        project = get_object_or_404(
            ProfileProject,
            profileproject_id=project_id,
            profile_snapshot__user=request.user
        )

        images = ProjectImage.objects.filter(
            project=project
        ).order_by(
            "position",
            "-is_primary"
        )

        serializer = ProjectImageSerializer(
            images,
            many=True
        )

        return Response({
            "message": "Project images fetched successfully",
            "data": serializer.data
        })

    def post(self, request, project_id):

        data = request.data.copy()
        data["project_id"] = project_id

        serializer = ProjectImageSerializer(
            data=data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Project image uploaded successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


# ============================================
# UPDATE + DELETE
# ============================================

class ProjectImageDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get_object(self, request, image_id):

        return get_object_or_404(
            ProjectImage,
            projectimage_id=image_id,
            project__profile_snapshot__user=request.user
        )

    def put(self, request, image_id):

        image = self.get_object(request, image_id)

        serializer = ProjectImageSerializer(
            image,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Project image updated successfully",
            "data": serializer.data
        })

    def delete(self, request, image_id):

        image = self.get_object(request, image_id)

        if image.public_id:
            cloudinary.uploader.destroy(image.public_id)

        image.delete()

        return Response({
            "message": "Project image deleted successfully"
        })


# ============================================
# REORDER
# ============================================

class ProjectImageReorderAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def post(self, request, project_id):

        project = get_object_or_404(
            ProfileProject,
            profileproject_id=project_id,
            profile_snapshot__user=request.user
        )

        order = request.data.get("order", [])

        for index, image_id in enumerate(order):

            ProjectImage.objects.filter(
                projectimage_id=image_id,
                project=project
            ).update(position=index)

        return Response({
            "message": "Project images reordered successfully"
        })
