# portfoliohub/services/duplicate_modules/basic_info_duplicate.py

from portfoliohub.models.profile_basic_info import (
    ProfileBasicInfo
)
from life_hub.utils import generate_ulid_with_prefix


class BasicInfoDuplicate:

    @staticmethod
    def copy(source_snapshot, new_snapshot):

        basic = getattr(
            source_snapshot,
            "basic_info",
            None
        )

        if not basic:
            return

        ProfileBasicInfo.objects.create(
            profilebasicinfo_id=generate_ulid_with_prefix("pbi"),
            profile_snapshot=new_snapshot,
            first_name=basic.first_name,
            last_name=basic.last_name,
            email=basic.email,
            phone=basic.phone,
            summary=basic.summary,
            website=basic.website,
            full_address=basic.full_address,
            image=basic.image,
            public_id=basic.public_id,
        )
