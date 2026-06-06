# portfoliohub/serializers/resume_project.py

from rest_framework import serializers
from django.shortcuts import get_object_or_404
from django.utils.text import slugify

from cloudinary.utils import cloudinary_url

from portfoliohub.models.resume_project import ResumeProject
from portfoliohub.models.profile_snapshot import ProfileSnapshot


class ResumeProjectSerializer(serializers.ModelSerializer):

    snapshot_id = serializers.CharField(
        write_only=True
    )

    profile_snapshot_id = serializers.CharField(
        source="profile_snapshot.profile_snapshot_id",
        read_only=True
    )

    profile_snapshot_title = serializers.CharField(
        source="profile_snapshot.title",
        read_only=True
    )

    pdf_url = serializers.SerializerMethodField()

    class Meta:
        model = ResumeProject

        fields = [
            "resume_id",

            # SNAPSHOT
            "snapshot_id",
            "profile_snapshot_id",
            "profile_snapshot_title",

            "title",
            "slug",

            "template_key",
            "font_family",
            "primary_color",
            "layout",

            "is_public",

            "is_pdf_generated",
            "last_generated_pdf",
            "pdf_url",

            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "resume_id",

            "profile_snapshot_id",
            "profile_snapshot_title",

            "slug",

            "is_pdf_generated",
            "last_generated_pdf",
            "pdf_url",

            "created_at",
            "updated_at",
        ]

    # ============================================
    # PDF URL
    # ============================================

    def get_pdf_url(self, obj):

        if not obj.pdf_public_id:
            return None

        url, _ = cloudinary_url(
            obj.pdf_public_id,
            resource_type="raw",
            secure=True
        )

        return url

    # ============================================
    # CREATE
    # ============================================

    def create(self, validated_data):

        request = self.context["request"]

        snapshot_id = validated_data.pop("snapshot_id")

        snapshot = get_object_or_404(
            ProfileSnapshot,
            profile_snapshot_id=snapshot_id,
            user=request.user
        )

        title = validated_data.get("title")

        base_slug = slugify(title)

        slug = base_slug
        counter = 1

        while ResumeProject.objects.filter(slug=slug).exists():

            slug = f"{base_slug}-{counter}"
            counter += 1

        return ResumeProject.objects.create(
            user=request.user,
            profile_snapshot=snapshot,
            slug=slug,
            **validated_data
        )

    # ============================================
    # UPDATE
    # ============================================

    def update(self, instance, validated_data):

        title = validated_data.get("title", instance.title)

        if title != instance.title:

            base_slug = slugify(title)

            slug = base_slug
            counter = 1

            while ResumeProject.objects.exclude(
                id=instance.id
            ).filter(slug=slug).exists():

                slug = f"{base_slug}-{counter}"
                counter += 1

            instance.slug = slug

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance
