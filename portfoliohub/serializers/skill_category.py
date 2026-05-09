from rest_framework import serializers
from portfoliohub.models.skill_category import SkillCategory


class SkillCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = SkillCategory
        fields = [
            "skillcategory_id",
            "name",
            "slug",
            "icon",
            "position",
            "is_active",
        ]

        read_only_fields = [
            "skillcategory_id"
        ]
