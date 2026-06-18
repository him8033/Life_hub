# portfoliohub/services/builders/basic_info_builder.py

from portfoliohub.services.builder_utils import (
    BuilderUtils
)


class BasicInfoBuilder:

    @staticmethod
    def build(snapshot):

        basic = getattr(
            snapshot,
            "basic_info",
            None
        )

        if not basic:
            return None

        return {
            "profilebasicinfo_id":
                basic.profilebasicinfo_id,

            "first_name":
                basic.first_name,

            "last_name":
                basic.last_name,

            "email":
                basic.email,

            "phone":
                basic.phone,

            "summary":
                basic.summary,

            "website":
                basic.website,

            "full_address":
                basic.full_address,

            "image":
                BuilderUtils.get_file_url(
                    basic.image
                ),
        }
