from rest_framework import serializers
from django.shortcuts import get_object_or_404

from portfoliohub.models.profile_snapshot import ProfileSnapshot
from portfoliohub.models.profile_hobby import ProfileHobby


class ProfileHobbySerializer(serializers.ModelSerializer):

    profile_snapshot_id = serializers.CharField(write_only=True)

    class Meta:
        model = ProfileHobby

        fields = [
            "profilehobby_id",
            "profile_snapshot_id",
            "hobby_name",
            "position",
            "created_at",
        ]

        read_only_fields = [
            "profilehobby_id",
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

        return ProfileHobby.objects.create(
            profile_snapshot=snapshot,
            **validated_data
        )
