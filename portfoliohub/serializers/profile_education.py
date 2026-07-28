from rest_framework import serializers
from django.shortcuts import get_object_or_404

from portfoliohub.models.profile_education import ProfileEducation
from portfoliohub.models.profile_snapshot import ProfileSnapshot


class ProfileEducationSerializer(serializers.ModelSerializer):

    profile_snapshot_id = serializers.CharField(write_only=True)

    class Meta:
        model = ProfileEducation
        fields = [
            "profileeducation_id",
            "profile_snapshot_id",
            "degree_name",
            "institution_name",
            "start_date",
            "end_date",
            "is_current",
            "score",
            "description",
            "full_address",
            "position",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "profileeducation_id",
            "created_at",
            "updated_at",
        ]

    # ============================================
    # VALIDATION
    # ============================================
    def validate(self, data):
        is_current = data.get("is_current")
        end_date = data.get("end_date")

        if is_current and end_date:
            raise serializers.ValidationError(
                "Current education should not have end_date"
            )

        return data

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
                ProfileEducation.objects.filter(
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

        return ProfileEducation.objects.create(
            profile_snapshot=snapshot,
            **validated_data
        )

    # ============================================
    # UPDATE
    # ============================================
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
