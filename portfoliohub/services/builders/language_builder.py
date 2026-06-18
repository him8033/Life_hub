# portfoliohub/services/builders/language_builder.py

class LanguageBuilder:

    @staticmethod
    def build(snapshot):

        languages = []

        for item in snapshot.languages.select_related(
            "language"
        ).all():

            languages.append({
                "profilelanguage_id":
                    item.profilelanguage_id,

                "language":
                    item.language.name,

                "code":
                    item.language.code,

                "icon":
                    item.language.icon,

                "proficiency":
                    item.proficiency,

                "position":
                    item.position,
            })

        return languages
