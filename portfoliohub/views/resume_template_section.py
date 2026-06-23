# portfoliohub/views/resume_template_section.py

from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from life_hub.renderers import UserRenderer

from portfoliohub.models.resume_template import (
    ResumeTemplate
)
from portfoliohub.models.master_section import (
    MasterSection
)
from portfoliohub.models.resume_template_section import (
    ResumeTemplateSection
)

from portfoliohub.serializers.resume_template_section import (
    ResumeTemplateSectionSerializer
)


class ResumeTemplateSectionAPIView(APIView):

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def _sync_sections(self, template):

        master_sections = MasterSection.objects.filter(
            is_active=True
        )

        existing_section_ids = set(
            template.sections.values_list(
                "section_id",
                flat=True
            )
        )

        missing_sections = []

        current_max_position = (
            template.sections.count()
        )

        for index, section in enumerate(
            master_sections,
            start=current_max_position + 1
        ):

            if section.id not in existing_section_ids:

                missing_sections.append(
                    ResumeTemplateSection(
                        template=template,
                        section=section,
                        is_required=False,
                        is_visible=False,
                        position=index
                    )
                )

        if missing_sections:

            for obj in missing_sections:
                obj.save()

    def get(self, request, template_id):

        template = get_object_or_404(
            ResumeTemplate,
            template_id=template_id
        )

        self._sync_sections(template)

        sections = (
            template.sections
            .select_related("section")
            .order_by("position")
        )

        serializer = ResumeTemplateSectionSerializer(
            sections,
            many=True
        )

        return Response({
            "message": "Sections fetched successfully",
            "data": serializer.data
        })


class ResumeTemplateSectionDetailAPIView(
    APIView
):

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get_object(
        self,
        template_id,
        section_id
    ):
        return get_object_or_404(
            ResumeTemplateSection.objects.select_related(
                "section",
                "template"
            ),
            resumetemplatesection_id=section_id,
            template__template_id=template_id
        )

    def get(
        self,
        request,
        template_id,
        section_id
    ):

        section = self.get_object(
            template_id,
            section_id
        )

        serializer = ResumeTemplateSectionSerializer(
            section
        )

        return Response({
            "message": "Section fetched successfully",
            "data": serializer.data
        })

    def put(
        self,
        request,
        template_id,
        section_id
    ):

        if not request.user.is_admin:

            return Response({
                "message": "Only admin can update sections"
            }, status=status.HTTP_403_FORBIDDEN)

        section = self.get_object(
            template_id,
            section_id
        )

        serializer = ResumeTemplateSectionSerializer(
            section,
            data=request.data,
            partial=True
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response({
            "message": "Section updated successfully",
            "data": serializer.data
        })
