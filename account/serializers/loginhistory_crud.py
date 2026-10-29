from rest_framework import serializers

from account.models import LoginHistory


class LoginHistoryListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing login history.
    """
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_id = serializers.CharField(source='user.user_id', read_only=True)

    class Meta:
        model = LoginHistory
        fields = [
            'loginhistory_id',
            'user_email',
            'user_id',
            'login_method',
            'success',
            'ip_address',
            'user_agent',
            'device',
            'browser',
            'operating_system',
            'failure_reason',
            'created_at',
        ]


class LoginHistoryDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for login history details.
    """
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_id = serializers.CharField(source='user.user_id', read_only=True)

    class Meta:
        model = LoginHistory
        fields = [
            'loginhistory_id',
            'user_email',
            'user_id',
            'login_method',
            'success',
            'ip_address',
            'user_agent',
            'device',
            'browser',
            'operating_system',
            'failure_reason',
            'created_at',
        ]
