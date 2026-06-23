# portfoliohub/serializers/resume_project.py

from rest_framework import serializers
from django.shortcuts import get_object_or_404

from cloudinary.utils import cloudinary_url

from portfoliohub.models.resume_project import ResumeProject
from portfoliohub.models.profile_snapshot import ProfileSnapshot
from portfoliohub.models.resume_template import ResumeTemplate
from portfoliohub.services.resume_project_create_service import (
    ResumeProjectCreateService
)


class ResumeProjectSerializer(serializers.ModelSerializer):

    snapshot_id = serializers.CharField(
        write_only=True,
        required=False,
        allow_null=True
    )

    template_id = serializers.CharField(
        write_only=True,
        required=True
    )

    resume_template_id = serializers.CharField(
        source="resume_template.template_id",
        read_only=True
    )

    resume_template_name = serializers.CharField(
        source="resume_template.name",
        read_only=True
    )

    profile_snapshot_id = serializers.CharField(
        source="profile_snapshot.profile_snapshot_id",
        read_only=True
    )

    profile_snapshot_title = serializers.CharField(
        source="profile_snapshot.title",
        read_only=True
    )

    pdf_url = serializers.SerializerMethodField()

    class Meta:

        model = ResumeProject

        fields = [
            "resume_id",

            "snapshot_id",
            "profile_snapshot_id",
            "profile_snapshot_title",

            "title",
            "slug",

            "template_id",
            "resume_template_id",
            "resume_template_name",

            "font_family",
            "primary_color",
            "layout",

            "is_public",

            "is_pdf_generated",
            "pdf_public_id",
            "pdf_url",

            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "resume_id",
            "slug",

            "profile_snapshot_id",
            "profile_snapshot_title",

            "resume_template_id",
            "resume_template_name",

            "is_pdf_generated",
            "pdf_public_id",
            "pdf_url",

            "created_at",
            "updated_at",
        ]

    def get_pdf_url(self, obj):

        if not obj.pdf_public_id:
            return None

        url, _ = cloudinary_url(
            obj.pdf_public_id,
            resource_type="raw",
            secure=True
        )

        return url

    def create(self, validated_data):

        request = self.context["request"]

        template_id = validated_data.pop(
            "template_id"
        )

        snapshot_id = validated_data.pop(
            "snapshot_id",
            None
        )

        template = get_object_or_404(
            ResumeTemplate,
            template_id=template_id,
            is_active=True
        )

        return ResumeProjectCreateService.create(
            user=request.user,
            resume_template=template,
            snapshot_id=snapshot_id,
            **validated_data
        )

    def update(self, instance, validated_data):

        title = validated_data.get(
            "title",
            instance.title
        )

        if title != instance.title:

            instance.slug = (
                ResumeProject.generate_unique_slug(
                    title,
                    exclude_id=instance.id
                )
            )

        template_id = validated_data.pop(
            "template_id",
            None
        )

        if template_id:

            template = get_object_or_404(
                ResumeTemplate,
                template_id=template_id,
                is_active=True
            )

            instance.resume_template = template

        snapshot_id = validated_data.pop(
            "snapshot_id",
            None
        )

        if snapshot_id:

            snapshot = get_object_or_404(
                ProfileSnapshot,
                profile_snapshot_id=snapshot_id,
                user=self.context["request"].user
            )

            instance.profile_snapshot = snapshot

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance
