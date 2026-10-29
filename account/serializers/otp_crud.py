from rest_framework import serializers

from account.models import OTP


class OTPListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing OTP records.
    """
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_id = serializers.CharField(source='user.user_id', read_only=True)
    purpose_name = serializers.CharField(source='purpose.name', read_only=True)
    purpose_slug = serializers.CharField(source='purpose.slug', read_only=True)

    class Meta:
        model = OTP
        fields = [
            'otp_id',
            'user_email',
            'user_id',
            'purpose_name',
            'purpose_slug',
            'attempts',
            'is_used',
            'expires_at',
            'used_at',
            'requested_ip',
            'requested_user_agent',
            'created_at',
            'updated_at',
        ]


class OTPDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for OTP details.
    """
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_id = serializers.CharField(source='user.user_id', read_only=True)
    purpose_name = serializers.CharField(source='purpose.name', read_only=True)
    purpose_slug = serializers.CharField(source='purpose.slug', read_only=True)

    class Meta:
        model = OTP
        fields = [
            'otp_id',
            'user_email',
            'user_id',
            'purpose_name',
            'purpose_slug',
            'attempts',
            'is_used',
            'expires_at',
            'used_at',
            'requested_ip',
            'requested_user_agent',
            'created_at',
            'updated_at',
        ]
