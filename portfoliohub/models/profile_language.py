from django.db import models
from life_hub.utils import generate_ulid_with_prefix

from portfoliohub.models.profile_snapshot import ProfileSnapshot
from portfoliohub.models.master_language import MasterLanguage


class ProfileLanguage(models.Model):
    id = models.BigAutoField(primary_key=True)

    profilelanguage_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        editable=False
    )

    profile_snapshot = models.ForeignKey(
        ProfileSnapshot,
        on_delete=models.CASCADE,
        related_name="languages"
    )

    language = models.ForeignKey(
        MasterLanguage,
        on_delete=models.CASCADE,
        related_name="profile_languages"
    )

    proficiency = models.CharField(
        max_length=30,
        choices=[
            ("basic", "Basic"),
            ("conversational", "Conversational"),
            ("professional", "Professional"),
            ("native", "Native"),
        ]
    )

    position = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["position", "language__name"]

        unique_together = [
            ("profile_snapshot", "language")
        ]

    def save(self, *args, **kwargs):

        if not self.profilelanguage_id:
            while True:
                candidate = generate_ulid_with_prefix("plng")

                if not ProfileLanguage.objects.filter(
                    profilelanguage_id=candidate
                ).exists():
                    self.profilelanguage_id = candidate
                    break

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.profile_snapshot.title} - {self.language.name}"
