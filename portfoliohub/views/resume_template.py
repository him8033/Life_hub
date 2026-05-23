from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticated,
)
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q

import cloudinary.uploader

from life_hub.renderers import UserRenderer

from portfoliohub.models.resume_template import ResumeTemplate
from portfoliohub.serializers.resume_template import (
    ResumeTemplateSerializer
)
from portfoliohub.pagination import (
    ResumeTemplatePagination
)


# ============================================
# PUBLIC LIST
# ============================================

class PublicResumeTemplateAPIView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request):

        queryset = ResumeTemplate.objects.filter(
            is_active=True
        ).order_by("name")

        serializer = ResumeTemplateSerializer(
            queryset,
            many=True
        )

        return Response({
            "message": "Resume templates fetched successfully",
            "data": serializer.data
        })


# ============================================
# LIST + CREATE
# ============================================

class ResumeTemplateAPIView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request):

        queryset = ResumeTemplate.objects.all()

        # =========================================
        # SEARCH
        # =========================================

        search = request.query_params.get(
            "search"
        )

        if search:

            queryset = queryset.filter(
                Q(name__icontains=search)
            )

        # =========================================
        # FILTERS
        # =========================================

        is_active = request.query_params.get(
            "is_active"
        )

        if is_active is not None:

            if is_active.lower() == "true":
                queryset = queryset.filter(
                    is_active=True
                )

            elif is_active.lower() == "false":
                queryset = queryset.filter(
                    is_active=False
                )

        is_premium = request.query_params.get(
            "is_premium"
        )

        if is_premium is not None:

            if is_premium.lower() == "true":
                queryset = queryset.filter(
                    is_premium=True
                )

            elif is_premium.lower() == "false":
                queryset = queryset.filter(
                    is_premium=False
                )

        is_ats_friendly = request.query_params.get(
            "is_ats_friendly"
        )

        if is_ats_friendly is not None:

            if is_ats_friendly.lower() == "true":
                queryset = queryset.filter(
                    is_ats_friendly=True
                )

            elif is_ats_friendly.lower() == "false":
                queryset = queryset.filter(
                    is_ats_friendly=False
                )

        # =========================================
        # SORTING
        # =========================================

        allowed_orderings = [
            "name",
            "-name",
            "created_at",
            "-created_at",
        ]

        ordering = request.query_params.get(
            "ordering",
            "-created_at"
        )

        if ordering not in allowed_orderings:
            ordering = "-created_at"

        queryset = queryset.order_by(ordering)

        # =========================================
        # PAGINATION
        # =========================================

        paginator = ResumeTemplatePagination()

        page = paginator.paginate_queryset(
            queryset,
            request,
            view=self
        )

        serializer = ResumeTemplateSerializer(
            page,
            many=True
        )

        return paginator.get_paginated_response(
            serializer.data
        )

    def post(self, request):

        if not request.user.is_admin:
            return Response({
                "message": "Only admin can create resume templates"
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = ResumeTemplateSerializer(
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response({
            "message": "Resume template created successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


# ============================================
# DETAIL + UPDATE + DELETE
# ============================================

class ResumeTemplateDetailAPIView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get_object(self, template_id):

        return get_object_or_404(
            ResumeTemplate,
            template_id=template_id
        )

    def get(self, request, template_id):

        template = self.get_object(
            template_id
        )

        serializer = ResumeTemplateSerializer(
            template
        )

        return Response({
            "message": "Resume template fetched successfully",
            "data": serializer.data
        })

    def put(self, request, template_id):

        if not request.user.is_admin:
            return Response({
                "message": "Only admin can update resume templates"
            }, status=status.HTTP_403_FORBIDDEN)

        template = self.get_object(
            template_id
        )

        serializer = ResumeTemplateSerializer(
            template,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response({
            "message": "Resume template updated successfully",
            "data": serializer.data
        })

    def delete(self, request, template_id):

        if not request.user.is_admin:
            return Response({
                "message": "Only admin can delete resume templates"
            }, status=status.HTTP_403_FORBIDDEN)

        template = self.get_object(
            template_id
        )

        if template.public_id:
            cloudinary.uploader.destroy(
                template.public_id
            )

        template.delete()

        return Response({
            "message": "Resume template deleted successfully"
        })
