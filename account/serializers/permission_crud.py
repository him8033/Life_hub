from rest_framework import serializers

from account.models import Permission


class PermissionListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing permissions.
    """

    class Meta:
        model = Permission
        fields = [
            'permission_id',
            'name',
            'slug',
            'module',
            'description',
            'is_active',
            'created_at',
            'updated_at',
        ]


class PermissionDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for permission details.
    """

    class Meta:
        model = Permission
        fields = [
            'permission_id',
            'name',
            'slug',
            'module',
            'description',
            'is_active',
            'created_at',
            'updated_at',
        ]


class PermissionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating permissions.
    """

    class Meta:
        model = Permission
        fields = [
            'name',
            'slug',
            'module',
            'description',
            'is_active',
        ]

    def validate_slug(self, value):
        """Validate slug format."""
        if not value or not value.strip():
            raise serializers.ValidationError("Slug is required")
        return value.strip()

    def validate_module(self, value):
        """Validate module format."""
        if value and not value.strip():
            raise serializers.ValidationError("Module cannot be empty")
        return value.strip() if value else value


class PermissionEditSerializer(serializers.ModelSerializer):
    """
    Serializer for editing permissions.
    """

    class Meta:
        model = Permission
        fields = [
            'name',
            'slug',
            'module',
            'description',
            'is_active',
        ]

    def validate_slug(self, value):
        """Validate slug format."""
        if value and not value.strip():
            raise serializers.ValidationError("Slug cannot be empty")
        return value.strip() if value else value

    def validate_module(self, value):
        """Validate module format."""
        if value and not value.strip():
            raise serializers.ValidationError("Module cannot be empty")
        return value.strip() if value else value


class PermissionDeleteSerializer(serializers.Serializer):
    """
    Serializer for permission deletion validation.
    """

    permanent = serializers.BooleanField(required=False, default=False)
    reason = serializers.CharField(required=False, allow_blank=True, max_length=500)
