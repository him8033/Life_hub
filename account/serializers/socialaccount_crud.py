from rest_framework import serializers

from account.models import SocialAccount


class SocialAccountListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing social accounts.
    """
    user_email = serializers.CharField(source='user.email', read_only=True)
    provider_name = serializers.CharField(source='provider.name', read_only=True)
    provider_slug = serializers.CharField(source='provider.slug', read_only=True)

    class Meta:
        model = SocialAccount
        fields = [
            'socialaccount_id',
            'user_email',
            'provider_name',
            'provider_slug',
            'provider_user_id',
            'provider_email',
            'provider_username',
            'avatar_url',
            'linked_at',
            'updated_at',
        ]


class SocialAccountDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for social account details.
    """
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_id = serializers.CharField(source='user.user_id', read_only=True)
    provider_name = serializers.CharField(source='provider.name', read_only=True)
    provider_slug = serializers.CharField(source='provider.slug', read_only=True)

    class Meta:
        model = SocialAccount
        fields = [
            'socialaccount_id',
            'user_id',
            'user_email',
            'provider_name',
            'provider_slug',
            'provider_user_id',
            'provider_email',
            'provider_username',
            'avatar_url',
            'provider_metadata',
            'linked_at',
            'updated_at',
        ]


class SocialAccountCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating social accounts manually.
    """
    user_id = serializers.CharField(write_only=True)
    provider_slug = serializers.CharField(write_only=True)

    class Meta:
        model = SocialAccount
        fields = [
            'user_id',
            'provider_slug',
            'provider_user_id',
            'provider_email',
            'provider_username',
            'avatar_url',
            'provider_metadata',
        ]

    def validate_provider_slug(self, value):
        """Validate provider exists."""
        from account.models import SocialProvider
        if not SocialProvider.objects.filter(slug=value, is_active=True).exists():
            raise serializers.ValidationError("Invalid or inactive provider")
        return value

    def validate_user_id(self, value):
        """Validate user exists."""
        from account.models import User
        if not User.objects.filter(user_id=value).exists():
            raise serializers.ValidationError("User not found")
        return value

    def validate_provider_metadata(self, value):
        """Validate provider metadata is a valid JSON object."""
        if value is not None:
            if not isinstance(value, dict):
                raise serializers.ValidationError("Provider metadata must be a valid JSON object")
        return value


class SocialAccountEditSerializer(serializers.ModelSerializer):
    """
    Serializer for editing social accounts.
    """

    class Meta:
        model = SocialAccount
        fields = [
            'provider_user_id',
            'provider_email',
            'provider_username',
            'avatar_url',
            'provider_metadata',
        ]

    def validate_provider_metadata(self, value):
        """Validate provider metadata is a valid JSON object."""
        if value is not None:
            if not isinstance(value, dict):
                raise serializers.ValidationError("Provider metadata must be a valid JSON object")
        return value


class SocialAccountDeleteSerializer(serializers.Serializer):
    """
    Serializer for social account deletion validation.
    """

    reason = serializers.CharField(required=False, allow_blank=True, max_length=500)
