from rest_framework import serializers
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

from portfoliohub.models.portfolio_theme import PortfolioTheme


class PortfolioThemeSerializer(serializers.ModelSerializer):

    preview_image_url = serializers.SerializerMethodField()

    class Meta:
        model = PortfolioTheme

        fields = [
            "theme_id",
            "name",
            "preview_image",
            "preview_image_url",
            "public_id",
            "is_premium",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "theme_id",
            "preview_image_url",
            "public_id",
            "created_at",
            "updated_at",
        ]

    # ============================================
    # IMAGE URL
    # ============================================

    def get_preview_image_url(self, obj):

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

        image = validated_data.pop("preview_image", None)

        instance = PortfolioTheme.objects.create(
            **validated_data
        )

        if image:
            upload = cloudinary.uploader.upload(
                image,
                folder="lifehub/portfolio_themes",
                resource_type="image",
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

        if image:

            # DELETE OLD IMAGE
            if instance.public_id:
                cloudinary.uploader.destroy(instance.public_id)

            upload = cloudinary.uploader.upload(
                image,
                folder="lifehub/portfolio_themes",
                resource_type="image",
            )

            instance.preview_image = upload["public_id"]
            instance.public_id = upload["public_id"]

        instance.save()

        return instance
