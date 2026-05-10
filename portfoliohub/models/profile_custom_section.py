from django.db import models
from life_hub.utils import generate_ulid_with_prefix

from portfoliohub.models.profile_snapshot import ProfileSnapshot


class ProfileCustomSection(models.Model):
    id = models.BigAutoField(primary_key=True)

    profilecustomsection_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        editable=False
    )

    profile_snapshot = models.ForeignKey(
        ProfileSnapshot,
        on_delete=models.CASCADE,
        related_name="custom_sections"
    )

    title = models.CharField(max_length=255)

    # DYNAMIC CONTENT
    content = models.JSONField(default=dict)

    position = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    # ============================================
    # AUTO ULID
    # ============================================

    def save(self, *args, **kwargs):
        if not self.profilecustomsection_id:

            while True:
                candidate = generate_ulid_with_prefix("cst")

                if not ProfileCustomSection.objects.filter(
                    profilecustomsection_id=candidate
                ).exists():
                    self.profilecustomsection_id = candidate
                    break

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
