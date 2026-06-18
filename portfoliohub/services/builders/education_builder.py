# portfoliohub/services/builders/education_builder.py

from portfoliohub.services.builder_utils import (
    BuilderUtils
)


class EducationBuilder:

    @staticmethod
    def build(snapshot):

        educations = []

        for item in snapshot.educations.all().order_by(
            "position",
            "-start_date"
        ):

            educations.append({
                "profileeducation_id":
                    item.profileeducation_id,

                "degree_name":
                    item.degree_name,

                "institution_name":
                    item.institution_name,

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

                "score":
                    item.score,

                "description":
                    item.description,

                "full_address":
                    item.full_address,

                "position":
                    item.position,
            })

        return educations
