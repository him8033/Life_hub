from rest_framework import serializers
from django.shortcuts import get_object_or_404

from portfoliohub.models.profile_snapshot import ProfileSnapshot
from portfoliohub.models.profile_custom_section import (
    ProfileCustomSection
)


class ProfileCustomSectionSerializer(serializers.ModelSerializer):

    profile_snapshot_id = serializers.CharField(write_only=True)

    class Meta:
        model = ProfileCustomSection

        fields = [
            "profilecustomsection_id",
            "profile_snapshot_id",
            "title",
            "content",
            "position",
            "created_at",
        ]

        read_only_fields = [
            "profilecustomsection_id",
            "created_at",
        ]

    # ============================================
    # VALIDATION
    # ============================================

    def validate_content(self, value):

        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Content must be valid JSON object"
            )

        return value

    # ============================================
    # CREATE
    # ============================================

    def create(self, validated_data):

        request = self.context["request"]

        snapshot_id = validated_data.pop("profile_snapshot_id")

        snapshot = get_object_or_404(
            ProfileSnapshot,
            profile_snapshot_id=snapshot_id,
            user=request.user
        )

        return ProfileCustomSection.objects.create(
            profile_snapshot=snapshot,
            **validated_data
        )
