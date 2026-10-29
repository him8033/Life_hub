from rest_framework import serializers

from account.models import UserStatus


# ============================================================
# STATUS CREATE
# ============================================================


class StatusCreateSerializer(serializers.ModelSerializer):
    """
    Admin serializer for creating a new user status.
    """

    class Meta:
        model = UserStatus
        fields = [
            "name",
            "slug",
            "description",
            "is_active",
        ]

    def validate_slug(self, value):
        """
        Validate that slug is unique and doesn't already exist.
        """
        if UserStatus.objects.filter(slug=value).exists():
            raise serializers.ValidationError(
                "A status with this slug already exists."
            )
        return value


# ============================================================
# STATUS EDIT
# ============================================================


class StatusEditSerializer(serializers.ModelSerializer):
    """
    Admin serializer for updating a user status.
    """

    class Meta:
        model = UserStatus
        fields = [
            "name",
            "slug",
            "description",
            "is_active",
        ]

    def validate_slug(self, value):
        """
        Validate that slug is unique (excluding current status).
        """
        # Get the instance being updated
        if self.instance:
            if UserStatus.objects.filter(slug=value).exclude(userstatus_id=self.instance.userstatus_id).exists():
                raise serializers.ValidationError(
                    "A status with this slug already exists."
                )
        else:
            if UserStatus.objects.filter(slug=value).exists():
                raise serializers.ValidationError(
                    "A status with this slug already exists."
                )
        return value


# ============================================================
# STATUS LIST
# ============================================================


class StatusListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing user statuses with basic information.
    """

    class Meta:
        model = UserStatus
        fields = [
            "userstatus_id",
            "name",
            "slug",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]


# ============================================================
# STATUS DETAIL
# ============================================================


class StatusDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed user status information.
    """

    class Meta:
        model = UserStatus
        fields = [
            "userstatus_id",
            "name",
            "slug",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]


# ============================================================
# STATUS DELETE
# ============================================================


class StatusDeleteSerializer(serializers.Serializer):
    """
    Admin serializer for deleting a user status.
    """

    permanent = serializers.BooleanField(
        default=False,
        help_text=(
            "Permanently delete status. "
            "Soft delete if False."
        ),
    )

    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        help_text="Reason for deletion",
    )
