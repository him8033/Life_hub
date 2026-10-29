from rest_framework import serializers

from account.models import OTPPurpose


class OTPPurposeListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing OTP purposes.
    """

    class Meta:
        model = OTPPurpose
        fields = [
            'otppurpose_id',
            'name',
            'slug',
            'description',
            'expiry_seconds',
            'max_attempts',
            'resend_cooldown_seconds',
            'is_active',
            'created_at',
            'updated_at',
        ]


class OTPPurposeDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for OTP purpose details.
    """

    class Meta:
        model = OTPPurpose
        fields = [
            'otppurpose_id',
            'name',
            'slug',
            'description',
            'expiry_seconds',
            'max_attempts',
            'resend_cooldown_seconds',
            'is_active',
            'created_at',
            'updated_at',
        ]


class OTPPurposeCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating OTP purposes.
    """

    class Meta:
        model = OTPPurpose
        fields = [
            'name',
            'slug',
            'description',
            'expiry_seconds',
            'max_attempts',
            'resend_cooldown_seconds',
            'is_active',
        ]

    def validate_slug(self, value):
        """Validate slug format."""
        if not value or not value.strip():
            raise serializers.ValidationError("Slug is required")
        return value.strip()

    def validate_expiry_seconds(self, value):
        """Validate expiry time is positive."""
        if value <= 0:
            raise serializers.ValidationError("Expiry time must be positive")
        return value

    def validate_max_attempts(self, value):
        """Validate max attempts is positive."""
        if value <= 0:
            raise serializers.ValidationError("Max attempts must be positive")
        return value

    def validate_resend_cooldown_seconds(self, value):
        """Validate resend cooldown is non-negative."""
        if value < 0:
            raise serializers.ValidationError("Resend cooldown cannot be negative")
        return value


class OTPPurposeEditSerializer(serializers.ModelSerializer):
    """
    Serializer for editing OTP purposes.
    """

    class Meta:
        model = OTPPurpose
        fields = [
            'name',
            'slug',
            'description',
            'expiry_seconds',
            'max_attempts',
            'resend_cooldown_seconds',
            'is_active',
        ]

    def validate_slug(self, value):
        """Validate slug format."""
        if value and not value.strip():
            raise serializers.ValidationError("Slug cannot be empty")
        return value.strip() if value else value

    def validate_expiry_seconds(self, value):
        """Validate expiry time is positive."""
        if value is not None and value <= 0:
            raise serializers.ValidationError("Expiry time must be positive")
        return value

    def validate_max_attempts(self, value):
        """Validate max attempts is positive."""
        if value is not None and value <= 0:
            raise serializers.ValidationError("Max attempts must be positive")
        return value

    def validate_resend_cooldown_seconds(self, value):
        """Validate resend cooldown is non-negative."""
        if value is not None and value < 0:
            raise serializers.ValidationError("Resend cooldown cannot be negative")
        return value


class OTPPurposeDeleteSerializer(serializers.Serializer):
    """
    Serializer for OTP purpose deletion validation.
    """

    permanent = serializers.BooleanField(required=False, default=False)
    reason = serializers.CharField(required=False, allow_blank=True, max_length=500)
