# portfoliohub/services/duplicate_modules/language_duplicate.py

from portfoliohub.models.profile_language import (
    ProfileLanguage
)
from life_hub.utils import generate_ulid_with_prefix

class LanguageDuplicate:

    @staticmethod
    def copy(source_snapshot, new_snapshot):

        languages = source_snapshot.languages.all()

        ProfileLanguage.objects.bulk_create([
            ProfileLanguage(
                profilelanguage_id=generate_ulid_with_prefix("plng"),
                profile_snapshot=new_snapshot,
                language=item.language,
                proficiency=item.proficiency,
                position=item.position,
            )
            for item in languages
        ])
