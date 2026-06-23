# portfoliohub/services/duplicate_modules/social_link_duplicate.py

from portfoliohub.models.profile_social_link import (
    ProfileSocialLink
)
from life_hub.utils import generate_ulid_with_prefix


class SocialLinkDuplicate:

    @staticmethod
    def copy(source_snapshot, new_snapshot):

        links = source_snapshot.social_links.all()

        ProfileSocialLink.objects.bulk_create([
            ProfileSocialLink(
                profilesociallink_id=generate_ulid_with_prefix("psl"),
                profile_snapshot=new_snapshot,
                platform_name=item.platform_name,
                url=item.url,
                icon=item.icon,
                is_primary=item.is_primary,
                is_active=item.is_active,
                position=item.position,
            )
            for item in links
        ])
