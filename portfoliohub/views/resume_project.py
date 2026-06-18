from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from portfoliohub.models.resume_project import ResumeProject
from portfoliohub.models.profile_snapshot import ProfileSnapshot
from portfoliohub.serializers.resume_project import (
    ResumeProjectSerializer
)

from life_hub.renderers import UserRenderer

import copy
import tempfile
import cloudinary.uploader

from reportlab.pdfgen import canvas

from portfoliohub.services.resume_builder import (
    ResumeBuilder
)


# ============================================
# LIST + CREATE
# ============================================

class ResumeProjectAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request):

        resumes = ResumeProject.objects.filter(
            user=request.user
        ).select_related(
            "profile_snapshot",
            "resume_template"
        )

        serializer = ResumeProjectSerializer(
            resumes,
            many=True
        )

        return Response({
            "message": "Resume projects fetched successfully",
            "data": serializer.data
        })

    def post(self, request):

        serializer = ResumeProjectSerializer(
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Resume project created successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


# ============================================
# DETAIL + UPDATE + DELETE
# ============================================

class ResumeProjectDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get_object(self, request, resume_id):

        return get_object_or_404(
            ResumeProject,
            resume_id=resume_id,
            user=request.user
        )

    def get(self, request, resume_id):

        resume = self.get_object(request, resume_id)

        serializer = ResumeProjectSerializer(resume)

        return Response({
            "message": "Resume fetched successfully",
            "data": serializer.data
        })

    def put(self, request, resume_id):

        resume = self.get_object(request, resume_id)

        serializer = ResumeProjectSerializer(
            resume,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Resume updated successfully",
            "data": serializer.data
        })

    def delete(self, request, resume_id):

        resume = self.get_object(request, resume_id)

        resume.delete()

        return Response({
            "message": "Resume deleted successfully"
        })


# ============================================
# DUPLICATE RESUME
# ============================================

class ResumeProjectDuplicateAPIView(APIView):

    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def post(self, request, resume_id):

        resume = get_object_or_404(
            ResumeProject,
            resume_id=resume_id,
            user=request.user
        )

        new_resume = ResumeProject.objects.create(
            user=request.user,
            profile_snapshot=resume.profile_snapshot,
            resume_template=resume.resume_template,
            title=f"{resume.title} Copy",
            font_family=resume.font_family,
            primary_color=resume.primary_color,
            layout=resume.layout,
            is_public=False
        )

        serializer = ResumeProjectSerializer(
            new_resume
        )

        return Response(
            {
                "message": "Resume duplicated successfully",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )


# ============================================
# GENERATE PDF
# ============================================

class ResumeProjectGeneratePDFAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def post(self, request, resume_id):

        resume = get_object_or_404(
            ResumeProject,
            resume_id=resume_id,
            user=request.user
        )

        # DELETE OLD PDF
        if resume.pdf_public_id:
            cloudinary.uploader.destroy(
                resume.pdf_public_id,
                resource_type="raw"
            )

        # ============================================
        # CREATE TEMP PDF
        # ============================================

        temp_pdf = tempfile.NamedTemporaryFile(
            suffix=".pdf",
            delete=False
        )

        p = canvas.Canvas(temp_pdf.name)

        p.drawString(
            100,
            750,
            f"Resume PDF for {resume.title}"
        )

        p.save()

        # ============================================
        # UPLOAD TO CLOUDINARY
        # ============================================

        upload = cloudinary.uploader.upload(
            temp_pdf.name,
            resource_type="raw",
            folder=f"lifehub/resumes/{resume.resume_id}"
        )

        # SAVE
        resume.last_generated_pdf = upload["public_id"]
        resume.pdf_public_id = upload["public_id"]

        resume.is_pdf_generated = True

        resume.save()

        return Response({
            "message": "PDF generated successfully"
        })


# ============================================
# PUBLIC RESUME VIEW
# ============================================

class PublicResumeProjectAPIView(APIView):
    renderer_classes = [UserRenderer]

    def get(self, request, slug):

        resume = get_object_or_404(
            ResumeProject,
            slug=slug,
            is_public=True
        )

        data = ResumeBuilder.build(resume)

        return Response({
            "message": "Resume preview fetched successfully",
            "data": data
        })
