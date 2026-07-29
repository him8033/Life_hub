from django.shortcuts import get_object_or_404

from rest_framework import serializers

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
    # VALIDATION
    # ============================================

    def validate(self, attrs):

        request = self.context["request"]

        # CREATE
        if self.instance is None:

            snapshot = get_object_or_404(
                ProfileSnapshot,
                profile_snapshot_id=attrs.get(
                    "profile_snapshot_id"
                ),
                user=request.user,
            )

        # UPDATE
        else:

            snapshot = self.instance.profile_snapshot

        platform_name = attrs.get(
            "platform_name",
            self.instance.platform_name if self.instance else None,
        )

        url = attrs.get(
            "url",
            self.instance.url if self.instance else None,
        )

        queryset = ProfileSocialLink.objects.filter(
            profile_snapshot=snapshot
        )

        # Ignore current record while updating
        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk
            )

        # Duplicate platform
        if queryset.filter(
            platform_name__iexact=platform_name
        ).exists():

            raise serializers.ValidationError({
                "platform_name": (
                    "This platform already exists."
                )
            })

        # Duplicate URL
        if queryset.filter(
            url__iexact=url
        ).exists():

            raise serializers.ValidationError({
                "url": (
                    "This URL already exists."
                )
            })

        return attrs

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
            user=request.user,
        )

        # ----------------------------------------
        # Only one primary link
        # ----------------------------------------

        if validated_data.get("is_primary", False):

            ProfileSocialLink.objects.filter(
                profile_snapshot=snapshot,
                is_primary=True,
            ).update(
                is_primary=False
            )

        # ----------------------------------------
        # Auto assign last position
        # ----------------------------------------

        if validated_data.get("position") is None:

            last = (
                ProfileSocialLink.objects.filter(
                    profile_snapshot=snapshot
                )
                .order_by("-position")
                .first()
            )

            validated_data["position"] = (
                (last.position + 1)
                if last and last.position is not None
                else 0
            )

        return ProfileSocialLink.objects.create(
            profile_snapshot=snapshot,
            **validated_data
        )

    # ============================================
    # UPDATE
    # ============================================

    def update(self, instance, validated_data):

        # ----------------------------------------
        # Only one primary link
        # ----------------------------------------

        if validated_data.get("is_primary", False):

            ProfileSocialLink.objects.filter(
                profile_snapshot=instance.profile_snapshot,
                is_primary=True,
            ).exclude(
                pk=instance.pk
            ).update(
                is_primary=False
            )

        for attr, value in validated_data.items():
            setattr(
                instance,
                attr,
                value
            )

        instance.save()

        return instance