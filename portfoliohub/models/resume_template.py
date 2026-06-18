from django.db import models
from cloudinary.models import CloudinaryField

from life_hub.utils import generate_ulid_with_prefix


class ResumeTemplate(models.Model):
    id = models.BigAutoField(primary_key=True)

    template_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        db_index=True
    )

    name = models.CharField(max_length=255)

    # CLOUDINARY
    preview_image = CloudinaryField(
        "image",
        blank=True,
        null=True
    )

    public_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    is_ats_friendly = models.BooleanField(default=False)

    is_premium = models.BooleanField(default=False)

    key = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):

        if not self.template_id:

            while True:
                candidate = generate_ulid_with_prefix("rtm")

                if not ResumeTemplate.objects.filter(
                    template_id=candidate
                ).exists():

                    self.template_id = candidate
                    break

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
