from rest_framework import serializers
from django.shortcuts import get_object_or_404

from portfoliohub.models.project_skill import ProjectSkill
from portfoliohub.models.profile_project import ProfileProject
from portfoliohub.models.master_skill import MasterSkill


class ProjectSkillSerializer(serializers.ModelSerializer):

    project_id = serializers.CharField(write_only=True)
    skill_id = serializers.CharField(write_only=True)

    skill_name = serializers.CharField(
        source="skill.name",
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

    class Meta:
        model = ProjectSkill
        fields = [
            "id",
            "project_id",
            "skill_id",

            "skill_name",
            "skill_icon",
            "category_name",
        ]

        read_only_fields = [
            "id",
            "skill_name",
            "skill_icon",
            "category_name",
        ]

    # ============================================
    # CREATE
    # ============================================

    def create(self, validated_data):

        request = self.context["request"]

        project_id = validated_data.pop("project_id")
        skill_id = validated_data.pop("skill_id")

        project = get_object_or_404(
            ProfileProject,
            profileproject_id=project_id,
            profile_snapshot__user=request.user
        )

        skill = get_object_or_404(
            MasterSkill,
            masterskill_id=skill_id
        )

        instance, created = ProjectSkill.objects.get_or_create(
            project=project,
            skill=skill
        )

        return instance
