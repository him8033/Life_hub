from rest_framework import serializers
from django.shortcuts import get_object_or_404

from portfoliohub.models.profile_strength import ProfileStrength
from portfoliohub.models.profile_snapshot import ProfileSnapshot


class ProfileStrengthSerializer(serializers.ModelSerializer):

    profile_snapshot_id = serializers.CharField(write_only=True)

    class Meta:
        model = ProfileStrength

        fields = [
            "profilestrength_id",
            "profile_snapshot_id",
            "title",
            "position",
            "created_at",
        ]

        read_only_fields = [
            "profilestrength_id",
            "created_at",
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

        # ----------------------------------------
        # Auto assign last position
        # ----------------------------------------
        if validated_data.get("position") is None:

            last = (
                ProfileStrength.objects.filter(
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

        return ProfileStrength.objects.create(
            profile_snapshot=snapshot,
            **validated_data
        )
