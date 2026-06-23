from rest_framework import serializers
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

from portfoliohub.models.portfolio_theme import PortfolioTheme
from portfoliohub.models.master_section import MasterSection
from portfoliohub.models.portfolio_theme_section import PortfolioThemeSection
from django.db import transaction


class PortfolioThemeSerializer(serializers.ModelSerializer):

    preview_image = serializers.ImageField(
        write_only=True,
        required=False
    )

    remove_image = serializers.BooleanField(
        write_only=True,
        required=False,
        default=False
    )

    preview_image_url = serializers.SerializerMethodField()

    class Meta:
        model = PortfolioTheme

        fields = [
            "theme_id",
            "name",
            "key",
            "description",

            "preview_image",
            "preview_image_url",
            "remove_image",

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

    @transaction.atomic
    def create(self, validated_data):

        image = validated_data.pop(
            "preview_image",
            None
        )

        validated_data.pop(
            "remove_image",
            False
        )

        theme = PortfolioTheme.objects.create(
            **validated_data
        )

        sections = MasterSection.objects.filter(
            is_active=True
        )

        for index, section in enumerate(
            sections,
            start=1
        ):

            PortfolioThemeSection.objects.create(
                theme=theme,
                section=section,
                is_required=False,
                is_visible=False,
                position=index
            )

        if image:

            upload = cloudinary.uploader.upload(
                image,
                folder="lifehub/portfolio_themes",
                resource_type="image"
            )

            theme.preview_image = upload["public_id"]
            theme.public_id = upload["public_id"]

            theme.save()

        return theme

    # ============================================
    # UPDATE
    # ============================================

    def update(self, instance, validated_data):

        image = validated_data.pop(
            "preview_image",
            None
        )

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

            instance.preview_image = None
            instance.public_id = None

        # REPLACE IMAGE
        elif image:

            if instance.public_id:
                cloudinary.uploader.destroy(
                    instance.public_id
                )

            upload = cloudinary.uploader.upload(
                image,
                folder="lifehub/portfolio_themes",
                resource_type="image"
            )

            instance.preview_image = upload["public_id"]
            instance.public_id = upload["public_id"]

        instance.save()

        return instance
