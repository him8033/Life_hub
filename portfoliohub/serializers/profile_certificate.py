from rest_framework import serializers
from django.shortcuts import get_object_or_404
import cloudinary.uploader

from portfoliohub.models.profile_snapshot import ProfileSnapshot
from portfoliohub.models.profile_certificate import ProfileCertificate


class ProfileCertificateSerializer(serializers.ModelSerializer):

    profile_snapshot_id = serializers.CharField(write_only=True)

    image = serializers.ImageField(
        write_only=True,
        required=False
    )

    remove_image = serializers.BooleanField(
        write_only=True,
        required=False,
        default=False
    )

    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProfileCertificate

        fields = [
            "profilecertificate_id",
            "profile_snapshot_id",
            "title",

            "issued_by",
            "issued_date",
            "expiry_date",

            "credential_id",
            "certificate_url",

            "image",
            "image_url",
            "remove_image",

            "description",
            "position",

            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "profilecertificate_id",
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
            width=500,
            crop="scale",
            quality="auto",
            fetch_format="auto"
        )

        return url

    # ============================================
    # VALIDATION
    # ============================================

    def validate(self, data):

        issued_date = data.get("issued_date")
        expiry_date = data.get("expiry_date")

        if issued_date and expiry_date:
            if expiry_date < issued_date:
                raise serializers.ValidationError(
                    "Expiry date cannot be before issued date"
                )

        return data

    # ============================================
    # CREATE
    # ============================================

    def create(self, validated_data):

        request = self.context["request"]

        snapshot_id = validated_data.pop("profile_snapshot_id")

        image = validated_data.pop("image", None)
        validated_data.pop("remove_image", False)

        snapshot = get_object_or_404(
            ProfileSnapshot,
            profile_snapshot_id=snapshot_id,
            user=request.user
        )

        instance = ProfileCertificate.objects.create(
            profile_snapshot=snapshot,
            **validated_data
        )

        # IMAGE UPLOAD
        if image:

            upload = cloudinary.uploader.upload(
                image,
                folder=f"lifehub/profiles/{snapshot.profile_snapshot_id}/certificates",
                resource_type="image"
            )

            instance.image = upload["public_id"]
            instance.public_id = upload["public_id"]

            instance.save()

        return instance

    # ============================================
    # UPDATE
    # ============================================

    def update(self, instance, validated_data):

        image = validated_data.pop("image", None)

        remove_image = validated_data.pop(
            "remove_image",
            False
        )

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # REMOVE IMAGE
        if remove_image:

            if instance.public_id:

                cloudinary.uploader.destroy(
                    instance.public_id
                )

            instance.image = None
            instance.public_id = None

        # REPLACE IMAGE
        elif image:

            if instance.public_id:
                cloudinary.uploader.destroy(instance.public_id)

            upload = cloudinary.uploader.upload(
                image,
                folder=f"lifehub/profiles/{instance.profile_snapshot.profile_snapshot_id}/certificates",
                resource_type="image"
            )

            instance.image = upload["public_id"]
            instance.public_id = upload["public_id"]

        instance.save()

        return instance
