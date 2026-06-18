# portfoliohub/services/builders/experience_builder.py

from portfoliohub.services.builder_utils import (
    BuilderUtils
)


class ExperienceBuilder:

    @staticmethod
    def build(snapshot):

        experiences = []

        for item in snapshot.experiences.all().order_by(
            "position",
            "priority",
            "-start_date"
        ):

            experiences.append({
                "profileexperience_id":
                    item.profileexperience_id,

                "company_name":
                    item.company_name,

                "role":
                    item.role,

                "employment_type":
                    item.employment_type,

                "start_date":
                    BuilderUtils.format_date(
                        item.start_date
                    ),

                "end_date":
                    BuilderUtils.format_date(
                        item.end_date
                    ),

                "is_current":
                    item.is_current,

                "description":
                    item.description,

                "full_address":
                    item.full_address,

                "company_logo":
                    BuilderUtils.get_file_url(
                        item.company_logo
                    ),

                "priority":
                    item.priority,

                "position":
                    item.position,
            })

        return experiences
