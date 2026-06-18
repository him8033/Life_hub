# portfoliohub/services/builders/social_link_builder.py

class SocialLinkBuilder:

    @staticmethod
    def build(snapshot):

        social_links = []

        for item in snapshot.social_links.filter(
            is_active=True
        ).order_by(
            "-is_primary",
            "position"
        ):

            social_links.append({
                "profilesociallink_id":
                    item.profilesociallink_id,

                "platform_name":
                    item.platform_name,

                "url":
                    item.url,

                "icon":
                    item.icon,

                "is_primary":
                    item.is_primary,

                "position":
                    item.position,
            })

        return social_links
