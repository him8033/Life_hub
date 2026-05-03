from django.db import models
from life_hub.utils import generate_ulid_with_prefix

from portfoliohub.models.profile_snapshot import ProfileSnapshot


class ProfileSocialLink(models.Model):
    id = models.BigAutoField(primary_key=True)

    profilesociallink_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        editable=False
    )

    profile_snapshot = models.ForeignKey(
        ProfileSnapshot,
        on_delete=models.CASCADE,
        related_name="social_links"
    )

    platform_name = models.CharField(max_length=100)
    url = models.URLField()

    icon = models.CharField(max_length=100, blank=True, null=True)

    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    position = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.profilesociallink_id:
            while True:
                candidate = generate_ulid_with_prefix("psl")
                if not ProfileSocialLink.objects.filter(profilesociallink_id=candidate).exists():
                    self.profilesociallink_id = candidate
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.platform_name} ({self.profile_snapshot.title})"
