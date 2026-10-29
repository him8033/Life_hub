from rest_framework import serializers

from account.models import UserSession


class UserSessionListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing user sessions.
    """
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_id = serializers.CharField(source='user.user_id', read_only=True)

    class Meta:
        model = UserSession
        fields = [
            'usersession_id',
            'user_email',
            'user_id',
            'device',
            'browser',
            'operating_system',
            'ip_address',
            'user_agent',
            'is_active',
            'last_activity_at',
            'expires_at',
            'revoked_at',
            'revoked_reason',
            'created_at',
            'updated_at',
        ]


class UserSessionDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for user session details.
    """
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_id = serializers.CharField(source='user.user_id', read_only=True)

    class Meta:
        model = UserSession
        fields = [
            'usersession_id',
            'user_email',
            'user_id',
            'session_identifier',
            'device',
            'browser',
            'operating_system',
            'ip_address',
            'user_agent',
            'is_active',
            'last_activity_at',
            'expires_at',
            'revoked_at',
            'revoked_reason',
            'created_at',
            'updated_at',
        ]


class UserSessionRevokeSerializer(serializers.Serializer):
    """
    Serializer for user session revocation.
    """

    reason = serializers.CharField(required=False, allow_blank=True, max_length=100)
