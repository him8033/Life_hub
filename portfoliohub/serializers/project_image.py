from rest_framework import serializers
from django.shortcuts import get_object_or_404

import cloudinary.uploader

from portfoliohub.models.project_image import ProjectImage
from portfoliohub.models.profile_project import ProfileProject


class ProjectImageSerializer(serializers.ModelSerializer):

    project_id = serializers.CharField(write_only=True)

    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProjectImage
        fields = [
            "projectimage_id",
            "project_id",

            "image",
            "image_url",

            "caption",
            "is_primary",
            "position",
            "created_at",
        ]

        read_only_fields = [
            "projectimage_id",
            "image_url",
            "created_at",
        ]

    # ============================================
    # IMAGE URL
    # ============================================

    def get_image_url(self, obj):

        from cloudinary.utils import cloudinary_url

        if not obj.public_id:
            return None

        url, _ = cloudinary_url(
            obj.public_id,
            quality="auto",
            fetch_format="auto"
        )

        return url

    # ============================================
    # CREATE
    # ============================================

    def create(self, validated_data):

        request = self.context["request"]

        project_id = validated_data.pop("project_id")

        image = validated_data.pop("image")

        project = get_object_or_404(
            ProfileProject,
            profileproject_id=project_id,
            profile_snapshot__user=request.user
        )

        instance = ProjectImage.objects.create(
            project=project,
            **validated_data
        )

        # ============================================
        # IMAGE UPLOAD
        # ============================================

        upload = cloudinary.uploader.upload(
            image,
            folder=f"lifehub/projects/{project.profileproject_id}/gallery",
            resource_type="image",
        )

        instance.image = upload["public_id"]
        instance.public_id = upload["public_id"]

        # PRIMARY IMAGE CONTROL
        if instance.is_primary:

            ProjectImage.objects.filter(
                project=project
            ).exclude(
                id=instance.id
            ).update(is_primary=False)

        instance.save()

        return instance

    # ============================================
    # UPDATE
    # ============================================

    def update(self, instance, validated_data):

        image = validated_data.pop("image", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # ============================================
        # IMAGE REPLACE
        # ============================================

        if image:

            if instance.public_id:
                cloudinary.uploader.destroy(instance.public_id)

            upload = cloudinary.uploader.upload(
                image,
                folder=f"lifehub/projects/{instance.project.profileproject_id}/gallery",
                resource_type="image",
            )

            instance.image = upload["public_id"]
            instance.public_id = upload["public_id"]

        # PRIMARY IMAGE CONTROL
        if instance.is_primary:

            ProjectImage.objects.filter(
                project=instance.project
            ).exclude(
                id=instance.id
            ).update(is_primary=False)

        instance.save()

        return instance
