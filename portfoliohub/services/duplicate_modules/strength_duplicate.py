# portfoliohub/services/duplicate_modules/strength_duplicate.py

from portfoliohub.models.profile_strength import (
    ProfileStrength
)
from life_hub.utils import generate_ulid_with_prefix


class StrengthDuplicate:

    @staticmethod
    def copy(source_snapshot, new_snapshot):

        strengths = source_snapshot.strengths.all()

        ProfileStrength.objects.bulk_create([
            ProfileStrength(
                profilestrength_id=generate_ulid_with_prefix("str"),
                profile_snapshot=new_snapshot,
                title=item.title,
                position=item.position,
            )
            for item in strengths
        ])
