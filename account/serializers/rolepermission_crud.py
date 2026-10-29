from rest_framework import serializers

from account.models import RolePermission


class RolePermissionListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing role permissions.
    """
    role_name = serializers.CharField(source='role.name', read_only=True)
    role_slug = serializers.CharField(source='role.slug', read_only=True)
    permission_name = serializers.CharField(source='permission.name', read_only=True)
    permission_slug = serializers.CharField(source='permission.slug', read_only=True)
    permission_module = serializers.CharField(source='permission.module', read_only=True)

    class Meta:
        model = RolePermission
        fields = [
            'rolepermission_id',
            'role_name',
            'role_slug',
            'permission_name',
            'permission_slug',
            'permission_module',
            'created_at',
            'updated_at',
        ]


class RolePermissionDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for role permission details.
    """
    role_name = serializers.CharField(source='role.name', read_only=True)
    role_slug = serializers.CharField(source='role.slug', read_only=True)
    role_id = serializers.CharField(source='role.role_id', read_only=True)
    permission_name = serializers.CharField(source='permission.name', read_only=True)
    permission_slug = serializers.CharField(source='permission.slug', read_only=True)
    permission_module = serializers.CharField(source='permission.module', read_only=True)
    permission_id = serializers.CharField(source='permission.permission_id', read_only=True)

    class Meta:
        model = RolePermission
        fields = [
            'rolepermission_id',
            'role_id',
            'role_name',
            'role_slug',
            'permission_id',
            'permission_name',
            'permission_slug',
            'permission_module',
            'created_at',
            'updated_at',
        ]


class RolePermissionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating role permissions.
    """
    role_slug = serializers.CharField(write_only=True)
    permission_slug = serializers.CharField(write_only=True)

    class Meta:
        model = RolePermission
        fields = [
            'role_slug',
            'permission_slug',
        ]

    def validate_role_slug(self, value):
        """Validate role exists and is active."""
        from account.models import Role
        if not Role.objects.filter(slug=value, is_active=True).exists():
            raise serializers.ValidationError("Invalid or inactive role")
        return value

    def validate_permission_slug(self, value):
        """Validate permission exists and is active."""
        from account.models import Permission
        if not Permission.objects.filter(slug=value, is_active=True).exists():
            raise serializers.ValidationError("Invalid or inactive permission")
        return value

    def validate(self, attrs):
        """Validate that the role-permission combination doesn't already exist."""
        from account.models import Role, Permission

        role = Role.objects.get(slug=attrs['role_slug'])
        permission = Permission.objects.get(slug=attrs['permission_slug'])

        if RolePermission.objects.filter(role=role, permission=permission).exists():
            raise serializers.ValidationError({
                "non_field_errors": ["This permission is already assigned to this role."]
            })

        return attrs


class RolePermissionDeleteSerializer(serializers.Serializer):
    """
    Serializer for role permission deletion validation.
    """

    reason = serializers.CharField(required=False, allow_blank=True, max_length=500)
