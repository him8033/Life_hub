# portfoliohub/services/builders/hobby_builder.py

class HobbyBuilder:

    @staticmethod
    def build(snapshot):

        hobbies = []

        for item in snapshot.hobbies.all():

            hobbies.append({
                "profilehobby_id":
                    item.profilehobby_id,

                "hobby_name":
                    item.hobby_name,

                "position":
                    item.position,
            })

        return hobbies
