# portfoliohub/services/duplicate_modules/skill_duplicate.py

from portfoliohub.models.profile_skill import (
    ProfileSkill
)
from life_hub.utils import generate_ulid_with_prefix


class SkillDuplicate:

    @staticmethod
    def copy(source_snapshot, new_snapshot):

        skills = source_snapshot.profile_skills.all()

        ProfileSkill.objects.bulk_create([
            ProfileSkill(
                profileskill_id=generate_ulid_with_prefix("psk"),
                profile_snapshot=new_snapshot,
                skill=item.skill,
                level=item.level,
                years_of_experience=item.years_of_experience,
                is_featured=item.is_featured,
                priority=item.priority,
                position=item.position,
            )
            for item in skills
        ])
