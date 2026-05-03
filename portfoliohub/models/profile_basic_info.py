from django.db import models
from cloudinary.models import CloudinaryField
from life_hub.utils import generate_ulid_with_prefix

from portfoliohub.models.profile_snapshot import ProfileSnapshot


class ProfileBasicInfo(models.Model):
    id = models.BigAutoField(primary_key=True)

    profilebasicinfo_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        editable=False
    )

    profile_snapshot = models.OneToOneField(
        ProfileSnapshot,
        on_delete=models.CASCADE,
        related_name="basic_info"
    )

    # BASIC DETAILS
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)

    summary = models.TextField(blank=True, null=True)
    full_address = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    # IMAGE
    image = CloudinaryField("image", blank=True, null=True)
    public_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        editable=False
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.profilebasicinfo_id:
            while True:
                candidate = generate_ulid_with_prefix("pbi")
                if not ProfileBasicInfo.objects.filter(profilebasicinfo_id=candidate).exists():
                    self.profilebasicinfo_id = candidate
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} ({self.profile_snapshot.title})"
