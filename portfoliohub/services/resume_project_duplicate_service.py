# portfoliohub/services/resume_project_duplicate_service.py

from django.db import transaction

from portfoliohub.models.resume_project import (
    ResumeProject
)

from portfoliohub.services.snapshot_duplicate_service import (
    SnapshotDuplicateService
)


class ResumeProjectDuplicateService:

    @staticmethod
    @transaction.atomic
    def duplicate(
        *,
        resume,
        user,
        duplicate_snapshot=False
    ):

        # =====================================
        # SNAPSHOT
        # =====================================

        snapshot = resume.profile_snapshot

        if duplicate_snapshot:

            snapshot = (
                SnapshotDuplicateService.duplicate(
                    source_snapshot=resume.profile_snapshot,
                    user=user
                )
            )

        # =====================================
        # RESUME
        # =====================================

        return ResumeProject.objects.create(
            user=user,
            profile_snapshot=snapshot,
            resume_template=resume.resume_template,

            title=f"{resume.title} Copy",

            font_family=resume.font_family,
            primary_color=resume.primary_color,
            layout=resume.layout,

            is_public=False
        )
