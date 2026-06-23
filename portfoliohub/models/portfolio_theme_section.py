# portfoliohub/models/portfolio_theme_section.py

from django.db import models

from portfoliohub.models.portfolio_theme import (
    PortfolioTheme
)
from portfoliohub.models.master_section import (
    MasterSection
)

from life_hub.utils import (
    generate_ulid_with_prefix
)


class PortfolioThemeSection(models.Model):

    id = models.BigAutoField(
        primary_key=True
    )

    portfoliothemesection_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        editable=False
    )

    theme = models.ForeignKey(
        PortfolioTheme,
        on_delete=models.CASCADE,
        related_name="sections"
    )

    section = models.ForeignKey(
        MasterSection,
        on_delete=models.CASCADE,
        related_name="portfolio_theme_sections"
    )

    is_required = models.BooleanField(
        default=False
    )

    is_visible = models.BooleanField(
        default=False
    )

    position = models.PositiveIntegerField(
        default=1
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        ordering = ["position"]

        unique_together = (
            "theme",
            "section"
        )

    def save(self, *args, **kwargs):

        if not self.portfoliothemesection_id:

            while True:

                candidate = generate_ulid_with_prefix(
                    "pts"
                )

                if not PortfolioThemeSection.objects.filter(
                    portfoliothemesection_id=candidate
                ).exists():

                    self.portfoliothemesection_id = candidate
                    break

        super().save(*args, **kwargs)

    def __str__(self):

        return (
            f"{self.theme.name} - "
            f"{self.section.name}"
        )
