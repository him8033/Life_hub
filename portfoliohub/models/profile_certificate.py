from django.db import models
from django.conf import settings
from cloudinary.models import CloudinaryField

from life_hub.utils import generate_ulid_with_prefix
from portfoliohub.models.profile_snapshot import ProfileSnapshot


class ProfileCertificate(models.Model):

    id = models.BigAutoField(primary_key=True)

    profilecertificate_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        editable=False
    )

    profile_snapshot = models.ForeignKey(
        ProfileSnapshot,
        on_delete=models.CASCADE,
        related_name="certificates"
    )

    title = models.CharField(max_length=255)

    issued_by = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    issued_date = models.DateField(
        blank=True,
        null=True
    )

    expiry_date = models.DateField(
        blank=True,
        null=True
    )

    credential_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    certificate_url = models.URLField(
        blank=True,
        null=True
    )

    image = CloudinaryField(
        "image",
        blank=True,
        null=True
    )

    public_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    position = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ============================================
    # ULID
    # ============================================

    def save(self, *args, **kwargs):

        if not self.profilecertificate_id:

            while True:
                candidate = generate_ulid_with_prefix("crt")

                if not ProfileCertificate.objects.filter(
                    profilecertificate_id=candidate
                ).exists():

                    self.profilecertificate_id = candidate
                    break

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
