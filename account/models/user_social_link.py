from django.db import models
from life_hub.utils import generate_ulid_with_prefix
from account.models.user_profile import UserProfile


class UserSocialLink(models.Model):
    id = models.BigAutoField(primary_key=True)

    usersociallink_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        editable=False
    )

    user_profile = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="social_links"
    )

    # Platform name
    platform_name = models.CharField(max_length=100)

    # Full URL (always)
    url = models.URLField()

    # UI Controls (for future use)
    is_primary = models.BooleanField(default=False)
    position = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["position"]
        indexes = [
            models.Index(fields=["usersociallink_id"]),
        ]

    def save(self, *args, **kwargs):
        if not self.usersociallink_id:
            while True:
                candidate = generate_ulid_with_prefix("usl")
                if not UserSocialLink.objects.filter(usersociallink_id=candidate).exists():
                    self.usersociallink_id = candidate
                    break

        # Auto position handling
        if not self.pk:
            last = (
                UserSocialLink.objects
                .filter(user_profile=self.user_profile)
                .order_by("-position")
                .first()
            )
            self.position = (last.position + 1) if last else 1

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.platform_name} - {self.url}"
