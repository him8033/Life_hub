from rest_framework import serializers
from django.shortcuts import get_object_or_404
from django.utils.text import slugify

from portfoliohub.models.portfolio_project import PortfolioProject
from portfoliohub.models.profile_snapshot import ProfileSnapshot


class PortfolioProjectSerializer(serializers.ModelSerializer):

    profile_snapshot_id = serializers.CharField(write_only=True)

    class Meta:
        model = PortfolioProject
        fields = [
            "portfolio_id",
            "profile_snapshot_id",
            "title",
            "slug",
            "theme_key",
            "custom_domain",
            "seo_title",
            "seo_description",
            "hero_title",
            "hero_subtitle",
            "is_public",
            "view_count",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "portfolio_id",
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
            "profile_snapshot_id"
        )

        snapshot = get_object_or_404(
            ProfileSnapshot,
            profile_snapshot_id=snapshot_id,
            user=request.user
        )

        title = validated_data.get("title")

        base_slug = slugify(title)
        slug = base_slug

        counter = 1

        while PortfolioProject.objects.filter(
            slug=slug
        ).exists():

            slug = f"{base_slug}-{counter}"
            counter += 1

        return PortfolioProject.objects.create(
            user=request.user,
            profile_snapshot=snapshot,
            slug=slug,
            **validated_data
        )

    # ============================================
    # UPDATE
    # ============================================

    def update(self, instance, validated_data):

        title = validated_data.get(
            "title",
            instance.title
        )

        if title != instance.title:

            base_slug = slugify(title)
            slug = base_slug

            counter = 1

            while PortfolioProject.objects.exclude(
                id=instance.id
            ).filter(slug=slug).exists():

                slug = f"{base_slug}-{counter}"
                counter += 1

            instance.slug = slug

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance
