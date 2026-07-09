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

    # =========================================
    # NAME
    # =========================================

    def validate_name(self, value):

        value = value.strip()

        queryset = MasterLanguage.objects.filter(
            name__iexact=value
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "Language name already exists."
            )

        return value

    # =========================================
    # CODE
    # =========================================

    def validate_code(self, value):

        value = value.strip().lower()

        queryset = MasterLanguage.objects.filter(
            code__iexact=value
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "Language code already exists."
            )

        return value

    # =========================================
    # POSITION
    # =========================================

    def validate_position(self, value):

        if value < 1:
            raise serializers.ValidationError(
                "Position must be greater than 0."
            )

        return value
