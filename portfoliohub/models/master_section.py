from django.db import models

from life_hub.utils import generate_ulid_with_prefix


class MasterSection(models.Model):

    id = models.BigAutoField(primary_key=True)

    mastersection_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        editable=False
    )

    name = models.CharField(
        max_length=100
    )

    key = models.CharField(
        max_length=100,
        unique=True
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def save(self, *args, **kwargs):

        if not self.mastersection_id:

            while True:

                candidate = generate_ulid_with_prefix(
                    "msc"
                )

                if not MasterSection.objects.filter(
                    mastersection_id=candidate
                ).exists():

                    self.mastersection_id = candidate
                    break

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
