# portfoliohub/services/duplicate_modules/achievement_duplicate.py

from portfoliohub.models.profile_achievement import (
    ProfileAchievement
)
from life_hub.utils import generate_ulid_with_prefix


class AchievementDuplicate:

    @staticmethod
    def copy(source_snapshot, new_snapshot):

        achievements = source_snapshot.achievements.all()

        ProfileAchievement.objects.bulk_create([
            ProfileAchievement(
                profileachievement_id=generate_ulid_with_prefix("ach"),
                profile_snapshot=new_snapshot,
                title=item.title,
                description=item.description,
                position=item.position,
            )
            for item in achievements
        ])
