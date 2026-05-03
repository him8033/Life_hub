from rest_framework import serializers
from django.shortcuts import get_object_or_404

from portfoliohub.models.profile_social_link import ProfileSocialLink
from portfoliohub.models.profile_snapshot import ProfileSnapshot


class ProfileSocialLinkSerializer(serializers.ModelSerializer):

    profile_snapshot_id = serializers.CharField(write_only=True)

    class Meta:
        model = ProfileSocialLink
        fields = [
            "profilesociallink_id",
            "profile_snapshot_id",
            "platform_name",
            "url",
            "icon",
            "is_primary",
            "is_active",
            "position",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "profilesociallink_id",
            "created_at",
            "updated_at",
        ]

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

        # If primary → reset others
        if validated_data.get("is_primary", False):
            ProfileSocialLink.objects.filter(
                profile_snapshot=snapshot,
                is_primary=True
            ).update(is_primary=False)

        return ProfileSocialLink.objects.create(
            profile_snapshot=snapshot,
            **validated_data
        )

    # ============================================
    # UPDATE
    # ============================================
    def update(self, instance, validated_data):

        # Handle primary switch
        if validated_data.get("is_primary", False):
            ProfileSocialLink.objects.filter(
                profile_snapshot=instance.profile_snapshot,
                is_primary=True
            ).exclude(id=instance.id).update(is_primary=False)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
