from rest_framework import serializers
from portfoliohub.models.master_language import MasterLanguage


class MasterLanguageSerializer(serializers.ModelSerializer):

    class Meta:
        model = MasterLanguage

        fields = [
            "masterlanguage_id",
            "name",
            "slug",
            "code",
            "icon",
            "position",
            "is_active",
            "created_at",
        ]

        read_only_fields = [
            "masterlanguage_id",
            "slug",
            "created_at",
        ]
