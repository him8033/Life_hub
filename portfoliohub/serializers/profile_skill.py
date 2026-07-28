from rest_framework import serializers
from django.shortcuts import get_object_or_404

from portfoliohub.models.profile_skill import ProfileSkill
from portfoliohub.models.profile_snapshot import ProfileSnapshot
from portfoliohub.models.master_skill import MasterSkill


class ProfileSkillSerializer(serializers.ModelSerializer):

    profile_snapshot_id = serializers.CharField(write_only=True)
    skill_id = serializers.CharField(write_only=True)

    # ============================================
    # MASTER SKILL DATA
    # ============================================

    skill_value = serializers.CharField(
        source="skill.masterskill_id",
        read_only=True
    )

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
            "skill_value",
            "skill_name",
            "skill_slug",
            "skill_icon",
            "category_name",
            "image_url",

            # USER DATA
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

            "skill_value",
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
    # UNIQUE SKILL VALIDATION
    # ============================================

    def validate_unique_skill(
        self,
        snapshot,
        skill,
        exclude_id=None
    ):

        queryset = ProfileSkill.objects.filter(
            profile_snapshot=snapshot
        )

        if exclude_id:
            queryset = queryset.exclude(
                id=exclude_id
            )

        # Duplicate same skill only
        if queryset.filter(
            skill=skill
        ).exists():

            raise serializers.ValidationError({
                "skill_id": [
                    "This skill is already added to the profile."
                ]
            })

    # ============================================
    # VALIDATION
    # ============================================

    def validate(self, data):

        request = self.context["request"]

        skill_id = data.get("skill_id")

        # CREATE
        if not self.instance and skill_id:

            snapshot_id = data.get("profile_snapshot_id")

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

            self.validate_unique_skill(
                snapshot,
                skill
            )

        # UPDATE
        elif self.instance and skill_id:

            skill = get_object_or_404(
                MasterSkill,
                masterskill_id=skill_id,
                is_active=True
            )

            self.validate_unique_skill(
                self.instance.profile_snapshot,
                skill,
                exclude_id=self.instance.id
            )

        return data

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

        # Auto assign last position
        if validated_data.get("position") is None:

            last = (
                ProfileSkill.objects.filter(
                    profile_snapshot=snapshot
                )
                .order_by("-position")
                .first()
            )

            validated_data["position"] = (
                last.position + 1
                if last and last.position is not None
                else 0
            )

        return ProfileSkill.objects.create(
            profile_snapshot=snapshot,
            skill=skill,
            **validated_data
        )

    # ============================================
    # UPDATE
    # ============================================

    def update(self, instance, validated_data):

        if "skill_id" in validated_data:

            skill_id = validated_data.pop("skill_id")

            skill = get_object_or_404(
                MasterSkill,
                masterskill_id=skill_id,
                is_active=True
            )

            instance.skill = skill

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance
