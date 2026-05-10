from django.db import models

from life_hub.utils import generate_ulid_with_prefix
from portfoliohub.models.profile_snapshot import ProfileSnapshot


class ProfileAchievement(models.Model):

    id = models.BigAutoField(primary_key=True)

    profileachievement_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        editable=False
    )

    profile_snapshot = models.ForeignKey(
        ProfileSnapshot,
        on_delete=models.CASCADE,
        related_name="achievements"
    )

    title = models.CharField(max_length=255)

    description = models.TextField(
        blank=True,
        null=True
    )

    position = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    # ============================================
    # ULID
    # ============================================

    def save(self, *args, **kwargs):

        if not self.profileachievement_id:

            while True:
                candidate = generate_ulid_with_prefix("ach")

                if not ProfileAchievement.objects.filter(
                    profileachievement_id=candidate
                ).exists():

                    self.profileachievement_id = candidate
                    break

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
