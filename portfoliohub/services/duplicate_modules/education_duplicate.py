# portfoliohub/services/duplicate_modules/education_duplicate.py

from portfoliohub.models.profile_education import (
    ProfileEducation
)
from life_hub.utils import generate_ulid_with_prefix


class EducationDuplicate:

    @staticmethod
    def copy(source_snapshot, new_snapshot):

        educations = source_snapshot.educations.all()

        ProfileEducation.objects.bulk_create([
            ProfileEducation(
                profileeducation_id=generate_ulid_with_prefix("edu"),
                profile_snapshot=new_snapshot,
                degree_name=item.degree_name,
                institution_name=item.institution_name,
                start_date=item.start_date,
                end_date=item.end_date,
                is_current=item.is_current,
                score=item.score,
                description=item.description,
                full_address=item.full_address,
                position=item.position,
            )
            for item in educations
        ])
