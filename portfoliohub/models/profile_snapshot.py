from django.db import models
from django.conf import settings
from life_hub.utils import generate_ulid_with_prefix


class ProfileSnapshot(models.Model):
    id = models.BigAutoField(primary_key=True)

    profile_snapshot_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        editable=False
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile_snapshots"
    )

    title = models.CharField(max_length=255)
    target_role = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    # DUPLICATION ENGINE
    source_profile = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="clones"
    )

    version = models.IntegerField(default=1)

    # CONTROL FLAGS 
    # TODO: Currently there is no need is_template and is_public
    is_template = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)

    visibility = models.CharField(
        max_length=20,
        choices=[
            ("private", "Private"),
            ("public", "Public"),
        ],
        default="private"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.profile_snapshot_id:
            while True:
                candidate = generate_ulid_with_prefix("prf")
                if not ProfileSnapshot.objects.filter(profile_snapshot_id=candidate).exists():
                    self.profile_snapshot_id = candidate
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.user.email})"
