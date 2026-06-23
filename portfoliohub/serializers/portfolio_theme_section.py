from rest_framework import serializers

from portfoliohub.models.portfolio_theme_section import (
    PortfolioThemeSection
)
from portfoliohub.models.master_section import (
    MasterSection
)


class PortfolioThemeSectionSerializer(
    serializers.ModelSerializer
):

    section = serializers.SerializerMethodField()

    mastersection_id = serializers.CharField(
        write_only=True,
        required=False
    )

    class Meta:

        model = PortfolioThemeSection

        fields = [
            "portfoliothemesection_id",

            "mastersection_id",

            "section",

            "is_required",
            "is_visible",

            "position",

            "created_at",
        ]

        read_only_fields = [
            "portfoliothemesection_id",
            "section",
            "created_at",
        ]

    def get_section(self, obj):

        return {
            "mastersection_id": obj.section.mastersection_id,
            "name": obj.section.name,
            "key": obj.section.key,
            "description": obj.section.description,
            "is_active": obj.section.is_active,
        }

    def update(self, instance, validated_data):

        mastersection_id = validated_data.pop(
            "mastersection_id",
            None
        )

        if mastersection_id:

            instance.section = MasterSection.objects.get(
                mastersection_id=mastersection_id
            )

        for attr, value in validated_data.items():

            setattr(
                instance,
                attr,
                value
            )

        instance.save()

        return instance
