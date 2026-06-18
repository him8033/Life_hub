class AchievementBuilder:

    @staticmethod
    def build(snapshot):

        achievements = []

        for item in snapshot.achievements.all().order_by(
            "position"
        ):

            achievements.append({
                "profileachievement_id":
                    item.profileachievement_id,

                "title":
                    item.title,

                "description":
                    item.description,

                "position":
                    item.position,
            })

        return achievements
