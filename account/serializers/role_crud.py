from rest_framework import serializers

from account.models.role import Role


# ============================================================
# ROLE CREATE
# ============================================================


class RoleCreateSerializer(serializers.ModelSerializer):
    """
    Admin serializer for creating a new role.
    """

    class Meta:
        model = Role
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
        if Role.objects.filter(slug=value).exists():
            raise serializers.ValidationError(
                "A role with this slug already exists."
            )
        return value


# ============================================================
# ROLE EDIT
# ============================================================


class RoleEditSerializer(serializers.ModelSerializer):
    """
    Admin serializer for updating a role.
    """

    class Meta:
        model = Role
        fields = [
            "name",
            "slug",
            "description",
            "is_active",
        ]

    def validate_slug(self, value):
        """
        Validate that slug is unique (excluding current role).
        """
        # Get the instance being updated
        if self.instance:
            if Role.objects.filter(slug=value).exclude(role_id=self.instance.role_id).exists():
                raise serializers.ValidationError(
                    "A role with this slug already exists."
                )
        else:
            if Role.objects.filter(slug=value).exists():
                raise serializers.ValidationError(
                    "A role with this slug already exists."
                )
        return value


# ============================================================
# ROLE LIST
# ============================================================


class RoleListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing roles with basic information.
    """

    class Meta:
        model = Role
        fields = [
            "role_id",
            "name",
            "slug",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]


# ============================================================
# ROLE DETAIL
# ============================================================


class RoleDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed role information.
    """

    class Meta:
        model = Role
        fields = [
            "role_id",
            "name",
            "slug",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]


# ============================================================
# ROLE DELETE
# ============================================================


class RoleDeleteSerializer(serializers.Serializer):
    """
    Admin serializer for deleting a role.
    """

    permanent = serializers.BooleanField(
        default=False,
        help_text=(
            "Permanently delete role. "
            "Soft delete if False."
        ),
    )

    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        help_text="Reason for deletion",
    )
