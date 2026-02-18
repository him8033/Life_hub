# travelhub/models/spot_image.py

from django.db import models
from django.conf import settings
from cloudinary.models import CloudinaryField
from travelhub.models import TravelSpot
from life_hub.utils import generate_ulid_with_prefix


class SpotImage(models.Model):
    id = models.BigAutoField(primary_key=True)

    spotimage_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        db_index=True
    )

    travelspot = models.ForeignKey(
        TravelSpot,
        on_delete=models.CASCADE,
        related_name="images"
    )

    image = CloudinaryField("image")

    public_id = models.CharField(
        max_length=255,
        editable=False
    )

    caption = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    is_primary = models.BooleanField(default=False)
    position = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="spotimages_created"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="spotimages_updated"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["position"]
        indexes = [
            models.Index(fields=["spotimage_id"]),
            models.Index(fields=["is_primary"]),
        ]

    def save(self, *args, **kwargs):
        if not self.spotimage_id:
            while True:
                candidate = generate_ulid_with_prefix("img")
                if not SpotImage.objects.filter(spotimage_id=candidate).exists():
                    self.spotimage_id = candidate
                    break

        if not self.pk:
            last = (
                SpotImage.objects
                .filter(travelspot=self.travelspot, deleted_at__isnull=True)
                .order_by("-position")
                .first()
            )

            self.position = (last.position + 1) if last else 1
            if not last:
                self.is_primary = True

        super().save(*args, **kwargs)
