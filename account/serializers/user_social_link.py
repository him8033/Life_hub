from rest_framework import serializers
from account.models.user_social_link import UserSocialLink


# ============================================
# MAIN SERIALIZER
# ============================================

class UserSocialLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSocialLink
        fields = [
            "usersociallink_id",
            "platform_name",
            "url",
            "is_primary",
            "position",
            "is_active",
            "created_at",
        ]
        read_only_fields = [
            "usersociallink_id",
            "is_primary",
            "position",
            "created_at",
        ]

    def create(self, validated_data):
        profile = self.context["profile"]

        link = UserSocialLink.objects.create(
            user_profile=profile,
            **validated_data
        )

        return link


# ============================================
# REORDER SERIALIZER
# ============================================

class UserSocialLinkReorderItemSerializer(serializers.Serializer):
    usersociallink_id = serializers.CharField()
    position = serializers.IntegerField(min_value=1)


class UserSocialLinkReorderSerializer(serializers.Serializer):
    order = UserSocialLinkReorderItemSerializer(many=True)

    def validate(self, data):
        positions = [item["position"] for item in data["order"]]

        if len(positions) != len(set(positions)):
            raise serializers.ValidationError(
                "Duplicate positions not allowed")

        if sorted(positions) != list(range(1, len(positions) + 1)):
            raise serializers.ValidationError(
                "Positions must be continuous starting from 1"
            )

        return data
