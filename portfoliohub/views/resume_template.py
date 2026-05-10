from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny
)
from rest_framework import status
from django.shortcuts import get_object_or_404

from life_hub.renderers import UserRenderer
from portfoliohub.models.resume_template import ResumeTemplate
from portfoliohub.serializers.resume_template import (
    ResumeTemplateSerializer
)


# ============================================
# LIST + CREATE
# ============================================

class ResumeTemplateAPIView(APIView):
    renderer_classes = [UserRenderer]

    def get_permissions(self):

        if self.request.method == "POST":
            return [IsAuthenticated()]

        return [AllowAny()]

    # LIST
    def get(self, request):

        templates = ResumeTemplate.objects.filter(
            is_active=True
        ).order_by("name")

        serializer = ResumeTemplateSerializer(
            templates,
            many=True,
            context={"request": request}
        )

        return Response({
            "message": "Resume templates fetched successfully",
            "data": serializer.data
        })

    # CREATE (ADMIN)
    def post(self, request):

        serializer = ResumeTemplateSerializer(
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Resume template created successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


# ============================================
# DETAIL / UPDATE / DELETE
# ============================================

class ResumeTemplateDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get_object(self, template_id):

        return get_object_or_404(
            ResumeTemplate,
            template_id=template_id
        )

    # GET SINGLE
    def get(self, request, template_id):

        template = self.get_object(template_id)

        serializer = ResumeTemplateSerializer(
            template,
            context={"request": request}
        )

        return Response({
            "message": "Resume template fetched successfully",
            "data": serializer.data
        })

    # UPDATE
    def put(self, request, template_id):

        template = self.get_object(template_id)

        serializer = ResumeTemplateSerializer(
            template,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Resume template updated successfully",
            "data": serializer.data
        })

    # DELETE
    def delete(self, request, template_id):

        template = self.get_object(template_id)

        template.delete()

        return Response({
            "message": "Resume template deleted successfully"
        })
