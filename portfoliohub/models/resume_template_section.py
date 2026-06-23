# portfoliohub/models/resume_template_section.py

from django.db import models

from portfoliohub.models.resume_template import ResumeTemplate
from portfoliohub.models.master_section import MasterSection

from life_hub.utils import generate_ulid_with_prefix


class ResumeTemplateSection(models.Model):

    id = models.BigAutoField(primary_key=True)

    resumetemplatesection_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        editable=False
    )

    template = models.ForeignKey(
        ResumeTemplate,
        on_delete=models.CASCADE,
        related_name="sections"
    )

    section = models.ForeignKey(
        MasterSection,
        on_delete=models.PROTECT,
        related_name="template_sections",
        null=True,
        blank=True
    )

    is_required = models.BooleanField(default=False)

    is_visible = models.BooleanField(default=True)

    position = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=["template", "section"],
                name="unique_template_section"
            )
        ]

        ordering = ["position"]

    def save(self, *args, **kwargs):

        if not self.resumetemplatesection_id:

            while True:

                candidate = generate_ulid_with_prefix("rts")

                if not ResumeTemplateSection.objects.filter(
                    resumetemplatesection_id=candidate
                ).exists():

                    self.resumetemplatesection_id = candidate
                    break

        super().save(*args, **kwargs)
