from django.db import models
from django.conf import settings
from travelhub.utils import generate_ulid_with_prefix
from travelhub.models import SpotCategory


class TravelSpot(models.Model):
    # Internal DB ID (never exposed)
    id = models.BigAutoField(primary_key=True)

    # Public Company ID
    travelspot_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        db_index=True,
        null=True,      # TEMP
        blank=True      # TEMP
    )

    # Basic Info
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    short_description = models.TextField(null=True, blank=True)
    long_description = models.TextField(null=True, blank=True)

    entry_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Entry fee in local currency; 0 for free"
    )

    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)

    best_time_to_visit = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="e.g. Oct–Mar, Early Morning, Evenings"
    )

    full_address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, default='Delhi')

    # Location Coordinates
    latitude = models.DecimalField(
        max_digits=10, decimal_places=8, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=11, decimal_places=8, null=True, blank=True
    )

    # Categories
    categories = models.ManyToManyField(
        SpotCategory,
        related_name="travel_spots",
        blank=True
    )

    # Status
    is_active = models.BooleanField(default=True)

    # Auth tracking
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='travelspots_created'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='travelspots_updated'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["city"]),
            models.Index(fields=["slug"]),
        ]

    def save(self, *args, **kwargs):
        if not self.travelspot_id:
            while True:
                candidate = generate_ulid_with_prefix("trv")
                if not TravelSpot.objects.filter(travelspot_id=candidate).exists():
                    self.travelspot_id = candidate
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
