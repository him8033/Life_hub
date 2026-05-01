from django.db import models
from django.conf import settings
from cloudinary.models import CloudinaryField
from life_hub.utils import generate_ulid_with_prefix
from locations.models import (
    Country,
    State,
    District,
    SubDistrict,
    Village,
    Pincode
)


class UserProfile(models.Model):
    id = models.BigAutoField(primary_key=True)

    profile_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        editable=False
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    # Profile Image
    profile_image = CloudinaryField(
        "image",
        blank=True,
        null=True
    )

    public_id = models.CharField(
        max_length=255,
        editable=False,
        blank=True,
        null=True
    )

    # Personal Info
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    headline = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    # Structured Location
    country = models.ForeignKey(
        Country, on_delete=models.SET_NULL, null=True, blank=True)
    state = models.ForeignKey(
        State, on_delete=models.SET_NULL, null=True, blank=True)
    district = models.ForeignKey(
        District, on_delete=models.SET_NULL, null=True, blank=True)
    sub_district = models.ForeignKey(
        SubDistrict, on_delete=models.SET_NULL, null=True, blank=True)
    village = models.ForeignKey(
        Village, on_delete=models.SET_NULL, null=True, blank=True)
    pincode = models.ForeignKey(
        Pincode, on_delete=models.SET_NULL, null=True, blank=True)

    full_address = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.profile_id:
            while True:
                candidate = generate_ulid_with_prefix("usr")
                if not UserProfile.objects.filter(profile_id=candidate).exists():
                    self.profile_id = candidate
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.email
