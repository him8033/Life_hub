from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from life_hub.renderers import UserRenderer

from portfoliohub.models.portfolio_theme import (
    PortfolioTheme
)

from portfoliohub.models.master_section import (
    MasterSection
)

from portfoliohub.models.portfolio_theme_section import (
    PortfolioThemeSection
)

from portfoliohub.serializers.portfolio_theme_section import (
    PortfolioThemeSectionSerializer
)


class PortfolioThemeSectionAPIView(
    APIView
):

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def _sync_sections(self, theme):

        master_sections = (
            MasterSection.objects
            .filter(is_active=True)
        )

        existing_section_ids = set(
            theme.sections.values_list(
                "section_id",
                flat=True
            )
        )

        missing_sections = []

        current_max_position = (
            theme.sections.count()
        )

        next_position = (
            current_max_position + 1
        )

        for section in master_sections:

            if section.id not in existing_section_ids:

                missing_sections.append(
                    PortfolioThemeSection(
                        theme=theme,
                        section=section,
                        is_required=False,
                        is_visible=False,
                        position=next_position
                    )
                )

                next_position += 1

        if missing_sections:

            for obj in missing_sections:
                obj.save()

    def get(
        self,
        request,
        theme_id
    ):

        theme = get_object_or_404(
            PortfolioTheme,
            theme_id=theme_id
        )

        self._sync_sections(theme)

        sections = (
            theme.sections
            .select_related("section")
            .order_by("position")
        )

        serializer = PortfolioThemeSectionSerializer(
            sections,
            many=True
        )

        return Response({
            "message":
                "Theme sections fetched successfully",

            "data":
                serializer.data
        })


class PortfolioThemeSectionDetailAPIView(
    APIView
):

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get_object(
        self,
        theme_id,
        section_id
    ):

        return get_object_or_404(
            PortfolioThemeSection.objects.select_related(
                "section",
                "theme"
            ),
            portfoliothemesection_id=section_id,
            theme__theme_id=theme_id
        )

    def get(
        self,
        request,
        theme_id,
        section_id
    ):

        section = self.get_object(
            theme_id,
            section_id
        )

        serializer = PortfolioThemeSectionSerializer(
            section
        )

        return Response({
            "message":
                "Theme section fetched successfully",

            "data":
                serializer.data
        })

    def put(
        self,
        request,
        theme_id,
        section_id
    ):

        if not request.user.is_admin:

            return Response({
                "message":
                    "Only admin can update sections"
            }, status=status.HTTP_403_FORBIDDEN)

        section = self.get_object(
            theme_id,
            section_id
        )

        serializer = PortfolioThemeSectionSerializer(
            section,
            data=request.data,
            partial=True
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response({
            "message":
                "Theme section updated successfully",

            "data":
                serializer.data
        })
