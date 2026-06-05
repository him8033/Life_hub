from rest_framework import serializers
from django.shortcuts import get_object_or_404

import cloudinary.uploader

from cloudinary.utils import cloudinary_url

from portfoliohub.models.profile_snapshot import ProfileSnapshot
from portfoliohub.models.profile_project import ProfileProject


class ProfileProjectSerializer(serializers.ModelSerializer):

    profile_snapshot_id = serializers.CharField(
        write_only=True
    )

    thumbnail = serializers.ImageField(
        write_only=True,
        required=False
    )

    remove_thumbnail = serializers.BooleanField(
        write_only=True,
        required=False,
        default=False
    )

    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = ProfileProject

        fields = [

            "profileproject_id",

            "profile_snapshot_id",

            "project_name",

            "short_description",
            "full_description",

            "code_url",
            "live_url",

            "thumbnail",
            "thumbnail_url",
            "remove_thumbnail",

            "is_live",
            "is_featured",

            "priority",
            "position",

            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "profileproject_id",
            "thumbnail_url",
            "created_at",
            "updated_at",
        ]

    # ============================================
    # THUMBNAIL URL
    # ============================================

    def get_thumbnail_url(self, obj):

        if not obj.public_id:
            return None

        url, _ = cloudinary_url(
            obj.public_id,
            width=1000,
            height=700,
            crop="fill",
            quality="auto",
            fetch_format="auto"
        )

        return url

    # ============================================
    # CREATE
    # ============================================

    def create(self, validated_data):

        request = self.context["request"]

        snapshot_id = validated_data.pop(
            "profile_snapshot_id"
        )
        validated_data.pop("remove_thumbnail", False)

        snapshot = get_object_or_404(
            ProfileSnapshot,
            profile_snapshot_id=snapshot_id,
            user=request.user
        )

        image = validated_data.pop(
            "thumbnail",
            None
        )

        project = ProfileProject.objects.create(
            profile_snapshot=snapshot,
            **validated_data
        )

        # IMAGE UPLOAD
        if image:

            upload = cloudinary.uploader.upload(
                image,
                folder=f"lifehub/projects/{snapshot.profile_snapshot_id}",
                resource_type="image"
            )

            project.thumbnail = upload["public_id"]
            project.public_id = upload["public_id"]

            project.save()

        return project

    # ============================================
    # UPDATE
    # ============================================

    def update(self, instance, validated_data):

        image = validated_data.pop(
            "thumbnail",
            None
        )

        remove_thumbnail = validated_data.pop(
            "remove_thumbnail",
            False
        )

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # REMOVE IMAGE
        if remove_thumbnail:

            if instance.public_id:

                cloudinary.uploader.destroy(
                    instance.public_id
                )

            instance.thumbnail = None
            instance.public_id = None

        # REPLACE IMAGE
        elif image:

            if instance.public_id:
                cloudinary.uploader.destroy(
                    instance.public_id
                )

            upload = cloudinary.uploader.upload(
                image,
                folder=f"lifehub/projects/{instance.profile_snapshot.profile_snapshot_id}",
                resource_type="image"
            )

            instance.thumbnail = upload["public_id"]
            instance.public_id = upload["public_id"]

        instance.save()

        return instance
