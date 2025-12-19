from django.db import models
from django.conf import settings


class TravelSpot(models.Model):
    # Basic Info
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    short_description = models.TextField(null=True, blank=True)
    full_address = models.TextField(null=True, blank=True)

    city = models.CharField(max_length=100, default='Delhi')

    # Location Coordinates
    latitude = models.DecimalField(
        max_digits=10, decimal_places=8, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=11, decimal_places=8, null=True, blank=True
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

    def __str__(self):
        return self.name
