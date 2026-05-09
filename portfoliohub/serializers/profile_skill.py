from rest_framework import serializers
from django.shortcuts import get_object_or_404

from portfoliohub.models.profile_skill import ProfileSkill
from portfoliohub.models.profile_snapshot import ProfileSnapshot
from portfoliohub.models.master_skill import MasterSkill


class ProfileSkillSerializer(serializers.ModelSerializer):

    profile_snapshot_id = serializers.CharField(write_only=True)
    skill_id = serializers.CharField(write_only=True)

    # MASTER SKILL DATA
    skill_name = serializers.CharField(
        source="skill.name",
        read_only=True
    )

    skill_slug = serializers.CharField(
        source="skill.slug",
        read_only=True
    )

    skill_icon = serializers.CharField(
        source="skill.icon",
        read_only=True
    )

    category_name = serializers.CharField(
        source="skill.category.name",
        read_only=True
    )

    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProfileSkill
        fields = [

            "profileskill_id",

            "profile_snapshot_id",

            "skill",
            "skill_id",

            # MASTER SKILL INFO
            "skill_name",
            "skill_slug",
            "skill_icon",
            "category_name",
            "image_url",

            # USER CUSTOM DATA
            "level",
            "years_of_experience",
            "is_featured",

            "priority",
            "position",

            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "profileskill_id",
            "skill",

            "skill_name",
            "skill_slug",
            "skill_icon",
            "category_name",
            "image_url",

            "created_at",
            "updated_at",
        ]

    # ============================================
    # IMAGE URL
    # ============================================

    def get_image_url(self, obj):

        from cloudinary.utils import cloudinary_url

        if not obj.skill.public_id:
            return None

        url, _ = cloudinary_url(
            obj.skill.public_id,
            width=200,
            height=200,
            crop="fit",
            quality="auto",
            fetch_format="auto"
        )

        return url

    # ============================================
    # VALIDATE LEVEL
    # ============================================

    def validate_level(self, value):

        if value < 1 or value > 5:
            raise serializers.ValidationError(
                "Level must be between 1 and 5"
            )

        return value

    # ============================================
    # CREATE
    # ============================================

    def create(self, validated_data):

        request = self.context["request"]

        snapshot_id = validated_data.pop(
            "profile_snapshot_id"
        )

        skill_id = validated_data.pop(
            "skill_id"
        )

        snapshot = get_object_or_404(
            ProfileSnapshot,
            profile_snapshot_id=snapshot_id,
            user=request.user
        )

        skill = get_object_or_404(
            MasterSkill,
            masterskill_id=skill_id,
            is_active=True
        )

        # PREVENT DUPLICATE
        exists = ProfileSkill.objects.filter(
            profile_snapshot=snapshot,
            skill=skill
        ).exists()

        if exists:
            raise serializers.ValidationError({
                "skill": "Skill already added to this profile"
            })

        return ProfileSkill.objects.create(
            profile_snapshot=snapshot,
            skill=skill,
            **validated_data
        )
