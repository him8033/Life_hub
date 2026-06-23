# portfoliohub/serializers/resume_template_section.py

from rest_framework import serializers

from portfoliohub.models.resume_template_section import (
    ResumeTemplateSection
)


class ResumeTemplateSectionSerializer(
    serializers.ModelSerializer
):

    section = serializers.SerializerMethodField()

    class Meta:

        model = ResumeTemplateSection

        fields = [
            "resumetemplatesection_id",

            "section",

            "is_required",
            "is_visible",

            "position",

            "created_at",
        ]

        read_only_fields = [
            "resumetemplatesection_id",
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

        allowed_fields = [
            "is_required",
            "is_visible",
            "position",
        ]

        for field in allowed_fields:

            if field in validated_data:
                setattr(
                    instance,
                    field,
                    validated_data[field]
                )

        instance.save()

        return instance
