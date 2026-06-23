# portfoliohub/services/snapshot_duplicate_service.py

from django.db import transaction

from portfoliohub.models.profile_snapshot import ProfileSnapshot

from portfoliohub.services.duplicate_modules.basic_info_duplicate import (
    BasicInfoDuplicate
)
from portfoliohub.services.duplicate_modules.experience_duplicate import (
    ExperienceDuplicate
)
from portfoliohub.services.duplicate_modules.education_duplicate import (
    EducationDuplicate
)
from portfoliohub.services.duplicate_modules.skill_duplicate import (
    SkillDuplicate
)
from portfoliohub.services.duplicate_modules.project_duplicate import (
    ProjectDuplicate
)
from portfoliohub.services.duplicate_modules.certificate_duplicate import (
    CertificateDuplicate
)
from portfoliohub.services.duplicate_modules.achievement_duplicate import (
    AchievementDuplicate
)
from portfoliohub.services.duplicate_modules.language_duplicate import (
    LanguageDuplicate
)
from portfoliohub.services.duplicate_modules.hobby_duplicate import (
    HobbyDuplicate
)
from portfoliohub.services.duplicate_modules.strength_duplicate import (
    StrengthDuplicate
)
from portfoliohub.services.duplicate_modules.social_link_duplicate import (
    SocialLinkDuplicate
)
from portfoliohub.services.duplicate_modules.custom_section_duplicate import (
    CustomSectionDuplicate
)


class SnapshotDuplicateService:

    @staticmethod
    @transaction.atomic
    def duplicate(source_snapshot, user):

        # ==========================================
        # CREATE NEW SNAPSHOT
        # ==========================================

        new_snapshot = ProfileSnapshot.objects.create(
            user=user,
            title=f"{source_snapshot.title} Copy",
            target_role=source_snapshot.target_role,
            description=source_snapshot.description,
            source_profile=source_snapshot,
            version=source_snapshot.version + 1,
            is_template=source_snapshot.is_template,
            is_public=False,
            visibility=source_snapshot.visibility,
        )

        # ==========================================
        # DUPLICATE MODULES
        # ==========================================

        BasicInfoDuplicate.copy(
            source_snapshot,
            new_snapshot
        )

        ExperienceDuplicate.copy(
            source_snapshot,
            new_snapshot
        )

        EducationDuplicate.copy(
            source_snapshot,
            new_snapshot
        )

        SkillDuplicate.copy(
            source_snapshot,
            new_snapshot
        )

        ProjectDuplicate.copy(
            source_snapshot,
            new_snapshot
        )

        CertificateDuplicate.copy(
            source_snapshot,
            new_snapshot
        )

        AchievementDuplicate.copy(
            source_snapshot,
            new_snapshot
        )

        LanguageDuplicate.copy(
            source_snapshot,
            new_snapshot
        )

        HobbyDuplicate.copy(
            source_snapshot,
            new_snapshot
        )

        StrengthDuplicate.copy(
            source_snapshot,
            new_snapshot
        )

        SocialLinkDuplicate.copy(
            source_snapshot,
            new_snapshot
        )

        CustomSectionDuplicate.copy(
            source_snapshot,
            new_snapshot
        )

        return new_snapshot
