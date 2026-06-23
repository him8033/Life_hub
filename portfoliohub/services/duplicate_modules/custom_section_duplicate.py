# portfoliohub/services/duplicate_modules/custom_section_duplicate.py

from portfoliohub.models.profile_custom_section import (
    ProfileCustomSection
)
from life_hub.utils import generate_ulid_with_prefix


class CustomSectionDuplicate:

    @staticmethod
    def copy(source_snapshot, new_snapshot):

        sections = source_snapshot.custom_sections.all()

        ProfileCustomSection.objects.bulk_create([
            ProfileCustomSection(
                profilecustomsection_id=generate_ulid_with_prefix("cst"),
                profile_snapshot=new_snapshot,
                title=item.title,
                content=item.content,
                position=item.position,
            )
            for item in sections
        ])
