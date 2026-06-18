# portfoliohub/services/builders/custom_section_builder.py

class CustomSectionBuilder:

    @staticmethod
    def build(snapshot):

        custom_sections = []

        for item in snapshot.custom_sections.all().order_by(
            "position"
        ):

            custom_sections.append({
                "profilecustomsection_id":
                    item.profilecustomsection_id,

                "title":
                    item.title,

                "content":
                    item.content,

                "position":
                    item.position,
            })

        return custom_sections
