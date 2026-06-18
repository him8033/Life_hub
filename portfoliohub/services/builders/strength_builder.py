# portfoliohub/services/builders/strength_builder.py

class StrengthBuilder:

    @staticmethod
    def build(snapshot):

        strengths = []

        for item in snapshot.strengths.all():

            strengths.append({
                "profilestrength_id":
                    item.profilestrength_id,

                "title":
                    item.title,

                "position":
                    item.position,
            })

        return strengths
