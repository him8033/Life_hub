from rest_framework import serializers
from portfoliohub.models.profile_snapshot import ProfileSnapshot


# ============================================
# PROFILE SNAPSHOT SERIALIZER
# ============================================

class ProfileSnapshotSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProfileSnapshot
        fields = [
            "profile_snapshot_id",
            "title",
            "target_role",
            "description",
            "source_profile",
            "version",
            "is_template",
            "is_public",
            "visibility",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "profile_snapshot_id",
            "source_profile",
            "version",
            "created_at",
            "updated_at",
        ]

    # ============================================
    # CREATE SNAPSHOT
    # ============================================
    def create(self, validated_data):
        user = self.context["request"].user

        if not validated_data.get("title"):
            validated_data["title"] = "Untitled Snapshot"

        return ProfileSnapshot.objects.create(
            user=user,
            **validated_data
        )
