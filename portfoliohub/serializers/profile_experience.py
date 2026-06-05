from rest_framework import serializers
from django.shortcuts import get_object_or_404
import cloudinary.uploader

from portfoliohub.models.profile_experience import ProfileExperience
from portfoliohub.models.profile_snapshot import ProfileSnapshot


class ProfileExperienceSerializer(serializers.ModelSerializer):

    profile_snapshot_id = serializers.CharField(write_only=True)

    company_logo = serializers.ImageField(
        write_only=True,
        required=False
    )

    remove_company_logo = serializers.BooleanField(
        write_only=True,
        required=False,
        default=False
    )

    company_logo_url = serializers.SerializerMethodField()

    class Meta:
        model = ProfileExperience

        fields = [
            "profileexperience_id",
            "profile_snapshot_id",

            "company_name",
            "role",
            "employment_type",

            "start_date",
            "end_date",
            "is_current",

            "description",
            "full_address",

            "company_logo",
            "company_logo_url",
            "remove_company_logo",

            "priority",
            "position",

            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "profileexperience_id",
            "company_logo_url",
            "created_at",
            "updated_at",
        ]

    # ============================================
    # IMAGE URL
    # ============================================
    def get_company_logo_url(self, obj):
        from cloudinary.utils import cloudinary_url

        if not obj.public_id:
            return None

        url, _ = cloudinary_url(
            obj.public_id,
            width=200,
            height=200,
            crop="fit",
            quality="auto",
            fetch_format="auto"
        )
        return url

    # ============================================
    # VALIDATION
    # ============================================
    def validate(self, data):
        if data.get("is_current") and data.get("end_date"):
            raise serializers.ValidationError(
                "Current job should not have end_date"
            )
        return data

    # ============================================
    # CREATE
    # ============================================
    def create(self, validated_data):
        request = self.context["request"]

        snapshot_id = validated_data.pop("profile_snapshot_id")
        logo = validated_data.pop("company_logo", None)
        validated_data.pop("remove_company_logo", False)

        snapshot = get_object_or_404(
            ProfileSnapshot,
            profile_snapshot_id=snapshot_id,
            user=request.user
        )

        instance = ProfileExperience.objects.create(
            profile_snapshot=snapshot,
            **validated_data
        )

        # IMAGE HANDLE
        if logo:
            upload = cloudinary.uploader.upload(
                logo,
                folder=f"lifehub/profiles/{snapshot.profile_snapshot_id}/experience",
                resource_type="image",
            )

            instance.company_logo = upload["public_id"]
            instance.public_id = upload["public_id"]
            instance.save()

        return instance

    # ============================================
    # UPDATE
    # ============================================

    def update(self, instance, validated_data):

        logo = validated_data.pop(
            "company_logo",
            None
        )

        remove_company_logo = validated_data.pop(
            "remove_company_logo",
            False
        )

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # REMOVE IMAGE
        if remove_company_logo:

            if instance.public_id:

                cloudinary.uploader.destroy(
                    instance.public_id
                )

            instance.company_logo = None
            instance.public_id = None

        # REPLACE IMAGE
        elif logo:

            if instance.public_id:

                cloudinary.uploader.destroy(
                    instance.public_id
                )

            upload = cloudinary.uploader.upload(
                logo,
                folder=f"lifehub/profiles/{instance.profile_snapshot.profile_snapshot_id}/experience",
                resource_type="image"
            )

            instance.company_logo = upload["public_id"]
            instance.public_id = upload["public_id"]

        instance.save()

        return instance
