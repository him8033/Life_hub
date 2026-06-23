# portfoliohub/services/portfolio_project_duplicate_service.py

from django.db import transaction

from portfoliohub.models.portfolio_project import (
    PortfolioProject
)

from portfoliohub.services.snapshot_duplicate_service import (
    SnapshotDuplicateService
)


class PortfolioProjectDuplicateService:

    @staticmethod
    @transaction.atomic
    def duplicate(
        *,
        portfolio,
        user,
        duplicate_snapshot=False
    ):

        profile_snapshot = portfolio.profile_snapshot

        # =====================================
        # DUPLICATE SNAPSHOT
        # =====================================

        if duplicate_snapshot:

            profile_snapshot = (
                SnapshotDuplicateService.duplicate(
                    source_snapshot=portfolio.profile_snapshot,
                    user=user
                )
            )

        # =====================================
        # DUPLICATE PORTFOLIO
        # =====================================

        return PortfolioProject.objects.create(
            user=user,

            profile_snapshot=profile_snapshot,
            portfolio_theme=portfolio.portfolio_theme,

            title=f"{portfolio.title} Copy",

            custom_domain=None,

            seo_title=portfolio.seo_title,
            seo_description=portfolio.seo_description,

            hero_title=portfolio.hero_title,
            hero_subtitle=portfolio.hero_subtitle,

            is_public=False
        )
