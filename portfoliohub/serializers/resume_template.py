from rest_framework import serializers
import cloudinary.uploader

from portfoliohub.models.resume_template import ResumeTemplate


class ResumeTemplateSerializer(serializers.ModelSerializer):

    preview_image_url = serializers.SerializerMethodField()

    class Meta:
        model = ResumeTemplate

        fields = [
            "template_id",
            "name",
            "preview_image",
            "preview_image_url",
            "is_ats_friendly",
            "is_premium",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "template_id",
            "preview_image_url",
            "created_at",
            "updated_at",
        ]

    # ============================================
    # IMAGE URL
    # ============================================

    def get_preview_image_url(self, obj):

        from cloudinary.utils import cloudinary_url

        if not obj.public_id:
            return None

        url, _ = cloudinary_url(
            obj.public_id,
            width=1200,
            crop="scale",
            quality="auto",
            fetch_format="auto"
        )

        return url

    # ============================================
    # CREATE
    # ============================================

    def create(self, validated_data):

        image = validated_data.pop("preview_image", None)

        instance = ResumeTemplate.objects.create(
            **validated_data
        )

        if image:

            upload = cloudinary.uploader.upload(
                image,
                folder="lifehub/resume_templates/previews",
                resource_type="image"
            )

            instance.preview_image = upload["public_id"]
            instance.public_id = upload["public_id"]

            instance.save()

        return instance

    # ============================================
    # UPDATE
    # ============================================

    def update(self, instance, validated_data):

        image = validated_data.pop("preview_image", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # REPLACE IMAGE
        if image:

            if instance.public_id:
                cloudinary.uploader.destroy(instance.public_id)

            upload = cloudinary.uploader.upload(
                image,
                folder="lifehub/resume_templates/previews",
                resource_type="image"
            )

            instance.preview_image = upload["public_id"]
            instance.public_id = upload["public_id"]

        instance.save()

        return instance
