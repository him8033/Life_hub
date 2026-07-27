from django.shortcuts import get_object_or_404
from rest_framework import serializers
import cloudinary.uploader

from portfoliohub.models.profile_basic_info import ProfileBasicInfo
from portfoliohub.models.profile_snapshot import ProfileSnapshot


class ProfileBasicInfoSerializer(serializers.ModelSerializer):

    profile_snapshot_id = serializers.CharField(write_only=True)

    remove_image = serializers.BooleanField(
        write_only=True,
        required=False,
        default=False
    )

    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProfileBasicInfo

        fields = [
            "profilebasicinfo_id",
            "profile_snapshot_id",

            "first_name",
            "last_name",
            "email",
            "phone",
            "summary",
            "full_address",
            "website",

            "image",
            "image_url",
            "remove_image",

            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "profilebasicinfo_id",
            "image_url",
            "created_at",
            "updated_at",
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
            width=300,
            height=300,
            crop="fill",
            gravity="face",
            quality="auto",
            fetch_format="auto"
        )
        return url

    # ============================================
    # CREATE / UPDATE (UPSERT)
    # ============================================
    def create(self, validated_data):
        request = self.context["request"]
        snapshot_id = validated_data.pop("profile_snapshot_id")

        image = validated_data.pop(
            "image",
            None
        )

        remove_image = validated_data.pop(
            "remove_image",
            False
        )

        snapshot = get_object_or_404(
            ProfileSnapshot,
            profile_snapshot_id=snapshot_id,
            user=request.user
        )

        instance, created = ProfileBasicInfo.objects.update_or_create(
            profile_snapshot=snapshot,
            defaults=validated_data
        )

        # ============================================
        # REMOVE IMAGE
        # ============================================

        if remove_image:

            if instance.public_id:
                cloudinary.uploader.destroy(
                    instance.public_id
                )

            instance.image = None
            instance.public_id = None

        # ============================================
        # REPLACE / UPLOAD IMAGE
        # ============================================

        elif image:

            if instance.public_id:
                cloudinary.uploader.destroy(
                    instance.public_id
                )

            upload = cloudinary.uploader.upload(
                image,
                folder=f"lifehub/profiles/{snapshot.profile_snapshot_id}/basic_info",
                resource_type="image",
                transformation=[
                    {
                        "width": 500,
                        "height": 500,
                        "crop": "fill",
                        "gravity": "face"
                    },
                    {"quality": "auto"},
                    {"fetch_format": "auto"},
                ]
            )

            instance.image = upload["public_id"]
            instance.public_id = upload["public_id"]

        instance.save()

        return instance
