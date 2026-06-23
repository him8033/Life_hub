# portfoliohub/services/resume_project_create_service.py

from django.shortcuts import get_object_or_404

from portfoliohub.models.profile_snapshot import (
    ProfileSnapshot
)
from portfoliohub.models.resume_project import (
    ResumeProject
)


class ResumeProjectCreateService:

    @staticmethod
    def create(
        *,
        user,
        title,
        resume_template,
        snapshot_id=None,
        **extra_fields
    ):

        # =====================================
        # EXISTING SNAPSHOT
        # =====================================

        if snapshot_id:

            profile_snapshot = get_object_or_404(
                ProfileSnapshot,
                profile_snapshot_id=snapshot_id,
                user=user
            )

        # =====================================
        # AUTO CREATE SNAPSHOT
        # =====================================

        else:

            profile_snapshot = (
                ProfileSnapshot.objects.create(
                    user=user,
                    title=title,
                    target_role="",
                    description=""
                )
            )

        # =====================================
        # CREATE RESUME
        # =====================================

        return ResumeProject.objects.create(
            user=user,
            profile_snapshot=profile_snapshot,
            resume_template=resume_template,
            title=title,
            **extra_fields
        )
