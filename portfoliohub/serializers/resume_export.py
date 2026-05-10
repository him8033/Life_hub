from rest_framework import serializers
from django.shortcuts import get_object_or_404

import cloudinary.uploader
from cloudinary.utils import cloudinary_url

from portfoliohub.models.resume_export import ResumeExport
from portfoliohub.models.resume_project import ResumeProject


class ResumeExportSerializer(serializers.ModelSerializer):

    resume_id = serializers.CharField(write_only=True)

    exported_file_url = serializers.SerializerMethodField()

    class Meta:
        model = ResumeExport

        fields = [
            "id",
            "resume_id",
            "exported_file",
            "exported_file_url",
            "public_id",
            "export_type",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "exported_file_url",
            "public_id",
            "created_at",
        ]

    # ============================================
    # FILE URL
    # ============================================

    def get_exported_file_url(self, obj):

        if not obj.public_id:
            return None

        url, _ = cloudinary_url(
            obj.public_id,
            resource_type="raw",
            secure=True
        )

        return url

    # ============================================
    # CREATE
    # ============================================

    def create(self, validated_data):

        request = self.context["request"]

        resume_id = validated_data.pop("resume_id")

        file = validated_data.pop("exported_file", None)

        resume = get_object_or_404(
            ResumeProject,
            resume_id=resume_id,
            user=request.user
        )

        instance = ResumeExport.objects.create(
            resume=resume,
            export_type=validated_data.get("export_type", "pdf")
        )

        if file:

            upload = cloudinary.uploader.upload(
                file,
                folder=f"lifehub/resumes/{resume.resume_id}/exports",
                resource_type="raw",
            )

            instance.exported_file = upload["public_id"]
            instance.public_id = upload["public_id"]
            instance.save()

        return instance
