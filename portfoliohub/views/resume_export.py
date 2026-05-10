from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404

from life_hub.renderers import UserRenderer
import cloudinary.uploader
from portfoliohub.models.resume_export import ResumeExport
from portfoliohub.models.resume_project import ResumeProject

from portfoliohub.serializers.resume_export import (
    ResumeExportSerializer
)


# ============================================
# LIST + CREATE
# ============================================

class ResumeExportAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    # LIST
    def get(self, request, resume_id):

        resume = get_object_or_404(
            ResumeProject,
            resume_id=resume_id,
            user=request.user
        )

        exports = ResumeExport.objects.filter(
            resume=resume
        ).order_by("-created_at")

        serializer = ResumeExportSerializer(
            exports,
            many=True
        )

        return Response({
            "message": "Resume exports fetched successfully",
            "data": serializer.data
        })

    # CREATE
    def post(self, request, resume_id):

        data = request.data.copy()

        data["resume_id"] = resume_id

        serializer = ResumeExportSerializer(
            data=data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Resume export uploaded successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


# ============================================
# DELETE
# ============================================

class ResumeExportDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get_object(self, request, export_id):

        return get_object_or_404(
            ResumeExport,
            id=export_id,
            resume__user=request.user
        )

    # DELETE
    def delete(self, request, export_id):

        export = self.get_object(request, export_id)

        # DELETE CLOUDINARY FILE
        if export.public_id:
            cloudinary.uploader.destroy(
                export.public_id,
                resource_type="raw"
            )

        export.delete()

        return Response({
            "message": "Resume export deleted successfully"
        })
