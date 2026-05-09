from django.db import models
from cloudinary.models import CloudinaryField
from life_hub.utils import generate_ulid_with_prefix

from portfoliohub.models.profile_snapshot import ProfileSnapshot


class ProfileExperience(models.Model):
    id = models.BigAutoField(primary_key=True)

    profileexperience_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        editable=False
    )

    profile_snapshot = models.ForeignKey(
        ProfileSnapshot,
        on_delete=models.CASCADE,
        related_name="experiences"
    )

    company_name = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    employment_type = models.CharField(max_length=100)

    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False)

    description = models.TextField(blank=True, null=True)
    full_address = models.TextField(blank=True, null=True)

    # IMAGE
    company_logo = CloudinaryField("image", blank=True, null=True)
    public_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        editable=False
    )

    priority = models.IntegerField(default=0)
    position = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.profileexperience_id:
            while True:
                candidate = generate_ulid_with_prefix("exp")
                if not ProfileExperience.objects.filter(profileexperience_id=candidate).exists():
                    self.profileexperience_id = candidate
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.role} @ {self.company_name}"
