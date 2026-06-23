# portfoliohub/services/duplicate_modules/hobby_duplicate.py

from portfoliohub.models.profile_hobby import (
    ProfileHobby
)
from life_hub.utils import generate_ulid_with_prefix


class HobbyDuplicate:

    @staticmethod
    def copy(source_snapshot, new_snapshot):

        hobbies = source_snapshot.hobbies.all()

        ProfileHobby.objects.bulk_create([
            ProfileHobby(
                profilehobby_id=generate_ulid_with_prefix("hby"),
                profile_snapshot=new_snapshot,
                hobby_name=item.hobby_name,
                position=item.position,
            )
            for item in hobbies
        ])
