from django.db import models
from django.conf import settings
from travelhub.models import TravelSpot


class TravelSpotView(models.Model):
    # Internal DB ID (never exposed)
    id = models.BigAutoField(primary_key=True)

    travelspot = models.ForeignKey(
        TravelSpot,
        on_delete=models.CASCADE,
        related_name="views"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    ip_address = models.GenericIPAddressField(null=True, blank=True)

    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["travelspot"]),
            models.Index(fields=["viewed_at"]),
        ]
