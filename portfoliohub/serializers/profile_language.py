from rest_framework import serializers
from django.shortcuts import get_object_or_404

from portfoliohub.models.profile_snapshot import ProfileSnapshot
from portfoliohub.models.profile_language import ProfileLanguage
from portfoliohub.models.master_language import MasterLanguage


class ProfileLanguageSerializer(serializers.ModelSerializer):

    profile_snapshot_id = serializers.CharField(write_only=True)

    language_id = serializers.CharField(write_only=True)

    language_value = serializers.CharField(
        source="language.masterlanguage_id",
        read_only=True
    )

    language_name = serializers.CharField(
        source="language.name",
        read_only=True
    )

    language_code = serializers.CharField(
        source="language.code",
        read_only=True
    )

    class Meta:
        model = ProfileLanguage

        fields = [
            "profilelanguage_id",

            "profile_snapshot_id",

            "language_id",
            "language_value",
            "language_name",
            "language_code",

            "proficiency",
            "position",

            "created_at",
        ]

        read_only_fields = [
            "profilelanguage_id",
            "language_name",
            "language_code",
            "created_at",
        ]

    # ============================================
    # VALIDATION
    # ============================================

    def validate(self, data):

        request = self.context["request"]

        language_id = data.get("language_id")

        # CREATE
        if not self.instance and language_id:

            snapshot_id = data.get("profile_snapshot_id")

            snapshot = get_object_or_404(
                ProfileSnapshot,
                profile_snapshot_id=snapshot_id,
                user=request.user
            )

            language = get_object_or_404(
                MasterLanguage,
                masterlanguage_id=language_id,
                is_active=True
            )

            exists = ProfileLanguage.objects.filter(
                profile_snapshot=snapshot,
                language=language
            ).exists()

            if exists:
                raise serializers.ValidationError({
                    "language_id": (
                        "This language is already added to the profile."
                    )
                })

        # UPDATE
        elif self.instance and language_id:

            language = get_object_or_404(
                MasterLanguage,
                masterlanguage_id=language_id,
                is_active=True
            )

            exists = ProfileLanguage.objects.filter(
                profile_snapshot=self.instance.profile_snapshot,
                language=language
            ).exclude(
                id=self.instance.id
            ).exists()

            if exists:
                raise serializers.ValidationError({
                    "language_id": (
                        "This language is already added to the profile."
                    )
                })

        return data

    # ============================================
    # CREATE
    # ============================================

    def create(self, validated_data):

        request = self.context["request"]

        snapshot_id = validated_data.pop("profile_snapshot_id")
        language_id = validated_data.pop("language_id")

        snapshot = get_object_or_404(
            ProfileSnapshot,
            profile_snapshot_id=snapshot_id,
            user=request.user
        )

        language = get_object_or_404(
            MasterLanguage,
            masterlanguage_id=language_id,
            is_active=True
        )

        return ProfileLanguage.objects.create(
            profile_snapshot=snapshot,
            language=language,
            **validated_data
        )

    # ============================================
    # UPDATE
    # ============================================

    def update(self, instance, validated_data):

        if "language_id" in validated_data:

            language = get_object_or_404(
                MasterLanguage,
                masterlanguage_id=validated_data.pop("language_id"),
                is_active=True
            )

            instance.language = language

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance
