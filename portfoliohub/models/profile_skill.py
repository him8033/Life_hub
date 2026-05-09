from django.db import models

from life_hub.utils import generate_ulid_with_prefix

from portfoliohub.models.profile_snapshot import ProfileSnapshot
from portfoliohub.models.master_skill import MasterSkill


class ProfileSkill(models.Model):
    id = models.BigAutoField(primary_key=True)

    profileskill_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        editable=False
    )

    profile_snapshot = models.ForeignKey(
        ProfileSnapshot,
        on_delete=models.CASCADE,
        related_name="profile_skills"
    )

    # MASTER SKILL
    skill = models.ForeignKey(
        MasterSkill,
        on_delete=models.CASCADE,
        related_name="profile_skills"
    )

    # USER CUSTOMIZATION
    level = models.IntegerField(default=3)

    years_of_experience = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=0
    )

    is_featured = models.BooleanField(default=False)

    priority = models.IntegerField(default=0)
    position = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [
            ("profile_snapshot", "skill")
        ]

    def save(self, *args, **kwargs):

        if not self.profileskill_id:

            while True:

                candidate = generate_ulid_with_prefix("psk")

                if not ProfileSkill.objects.filter(
                    profileskill_id=candidate
                ).exists():

                    self.profileskill_id = candidate
                    break

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.profile_snapshot.title} → {self.skill.name}"
