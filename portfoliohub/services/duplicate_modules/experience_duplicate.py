# portfoliohub/services/duplicate_modules/experience_duplicate.py

from portfoliohub.models.profile_experience import (
    ProfileExperience
)
from life_hub.utils import generate_ulid_with_prefix


class ExperienceDuplicate:

    @staticmethod
    def copy(source_snapshot, new_snapshot):

        experiences = source_snapshot.experiences.all()

        ProfileExperience.objects.bulk_create([
            ProfileExperience(
                profileexperience_id=generate_ulid_with_prefix("exp"),
                profile_snapshot=new_snapshot,
                company_name=item.company_name,
                role=item.role,
                employment_type=item.employment_type,
                start_date=item.start_date,
                end_date=item.end_date,
                is_current=item.is_current,
                description=item.description,
                full_address=item.full_address,
                company_logo=item.company_logo,
                priority=item.priority,
                position=item.position,
            )
            for item in experiences
        ])
