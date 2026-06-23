from rest_framework import serializers
from django.shortcuts import get_object_or_404

from portfoliohub.models.portfolio_project import PortfolioProject
from portfoliohub.models.profile_snapshot import ProfileSnapshot
from portfoliohub.models.portfolio_theme import PortfolioTheme
from portfoliohub.services.portfolio_project_create_service import (
    PortfolioProjectCreateService
)


class PortfolioProjectSerializer(serializers.ModelSerializer):

    snapshot_id = serializers.CharField(
        write_only=True,
        required=False,
        allow_null=True
    )

    theme_id = serializers.CharField(
        write_only=True,
        required=False
    )

    profile_snapshot_id = serializers.CharField(
        source="profile_snapshot.profile_snapshot_id",
        read_only=True
    )

    profile_snapshot_title = serializers.CharField(
        source="profile_snapshot.title",
        read_only=True
    )

    portfolio_theme_id = serializers.CharField(
        source="portfolio_theme.theme_id",
        read_only=True
    )

    portfolio_theme_name = serializers.CharField(
        source="portfolio_theme.name",
        read_only=True
    )

    class Meta:
        model = PortfolioProject

        fields = [
            "portfolio_id",

            # SNAPSHOT
            "snapshot_id",
            "profile_snapshot_id",
            "profile_snapshot_title",

            # BASIC
            "title",
            "slug",

            # THEME
            "theme_id",
            "portfolio_theme_id",
            "portfolio_theme_name",

            # DOMAIN
            "custom_domain",

            # SEO
            "seo_title",
            "seo_description",

            # HERO
            "hero_title",
            "hero_subtitle",

            # CONTROL
            "is_public",

            # ANALYTICS
            "view_count",

            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "portfolio_id",

            "profile_snapshot_id",
            "profile_snapshot_title",

            "portfolio_theme_id",
            "portfolio_theme_name",

            "slug",
            "view_count",

            "created_at",
            "updated_at",
        ]

    # ============================================
    # CREATE
    # ============================================

    def create(self, validated_data):

        request = self.context["request"]

        snapshot_id = validated_data.pop(
            "snapshot_id",
            None
        )

        theme_id = validated_data.pop(
            "theme_id",
            None
        )

        if not theme_id:
            raise serializers.ValidationError({
                "theme_id": "This field is required."
            })

        theme = get_object_or_404(
            PortfolioTheme,
            theme_id=theme_id,
            is_active=True
        )

        return PortfolioProjectCreateService.create(
            user=request.user,
            portfolio_theme=theme,
            snapshot_id=snapshot_id,
            **validated_data
        )

    # ============================================
    # UPDATE
    # ============================================

    def update(self, instance, validated_data):

        request = self.context["request"]

        title = validated_data.get(
            "title",
            instance.title
        )

        snapshot_id = validated_data.pop(
            "snapshot_id",
            None
        )

        theme_id = validated_data.pop(
            "theme_id",
            None
        )

        if snapshot_id:

            snapshot = get_object_or_404(
                ProfileSnapshot,
                profile_snapshot_id=snapshot_id,
                user=request.user
            )

            instance.profile_snapshot = snapshot

        if theme_id:

            theme = get_object_or_404(
                PortfolioTheme,
                theme_id=theme_id,
                is_active=True
            )

            instance.portfolio_theme = theme

        if title != instance.title:

            instance.slug = (
                PortfolioProject.generate_unique_slug(
                    title,
                    exclude_id=instance.id
                )
            )

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance
