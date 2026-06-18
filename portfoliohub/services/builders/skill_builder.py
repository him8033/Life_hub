# portfoliohub/services/builders/skill_builder.py

from portfoliohub.services.builder_utils import (
    BuilderUtils
)


class SkillBuilder:

    @staticmethod
    def build(snapshot):

        skills = []

        for item in snapshot.profile_skills.select_related(
            "skill",
            "skill__category"
        ).all().order_by(
            "position",
            "priority",
            "-is_featured"
        ):

            skills.append({
                "profileskill_id":
                    item.profileskill_id,

                "name":
                    item.skill.name,

                "slug":
                    item.skill.slug,

                "icon":
                    item.skill.icon,

                "image":
                    BuilderUtils.get_file_url(
                        item.skill.image
                    ),

                "category":
                    item.skill.category.name
                    if item.skill.category else None,

                "level":
                    item.level,

                "years_of_experience":
                    float(item.years_of_experience),

                "is_featured":
                    item.is_featured,

                "priority":
                    item.priority,

                "position":
                    item.position,
            })

        return skills
