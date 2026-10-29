from rest_framework import serializers

from account.models import SocialProvider


class SocialProviderListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing social providers.
    """

    class Meta:
        model = SocialProvider
        fields = [
            'socialprovider_id',
            'name',
            'slug',
            'description',
            'is_active',
            'created_at',
            'updated_at',
        ]


class SocialProviderDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for social provider details.
    """

    class Meta:
        model = SocialProvider
        fields = [
            'socialprovider_id',
            'name',
            'slug',
            'description',
            'is_active',
            'provider_metadata',
            'created_at',
            'updated_at',
        ]


class SocialProviderCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating social providers.
    """

    class Meta:
        model = SocialProvider
        fields = [
            'name',
            'slug',
            'description',
            'is_active',
            'provider_metadata',
        ]

    def validate_slug(self, value):
        """Validate slug format."""
        if not value or not value.strip():
            raise serializers.ValidationError("Slug is required")
        return value.strip()

    def validate_provider_metadata(self, value):
        """Validate provider metadata is a valid JSON object."""
        if value is not None:
            if not isinstance(value, dict):
                raise serializers.ValidationError("Provider metadata must be a valid JSON object")
        return value


class SocialProviderEditSerializer(serializers.ModelSerializer):
    """
    Serializer for editing social providers.
    """

    class Meta:
        model = SocialProvider
        fields = [
            'name',
            'slug',
            'description',
            'is_active',
            'provider_metadata',
        ]

    def validate_slug(self, value):
        """Validate slug format."""
        if value and not value.strip():
            raise serializers.ValidationError("Slug cannot be empty")
        return value.strip() if value else value

    def validate_provider_metadata(self, value):
        """Validate provider metadata is a valid JSON object."""
        if value is not None:
            if not isinstance(value, dict):
                raise serializers.ValidationError("Provider metadata must be a valid JSON object")
        return value


class SocialProviderDeleteSerializer(serializers.Serializer):
    """
    Serializer for social provider deletion validation.
    """

    permanent = serializers.BooleanField(required=False, default=False)
    reason = serializers.CharField(required=False, allow_blank=True, max_length=500)
