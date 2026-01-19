from django.db import models
from django.conf import settings
from travelhub.utils import generate_ulid_with_prefix


class SpotCategory(models.Model):
    # Internal DB ID
    id = models.BigAutoField(primary_key=True)

    # Public Category ID
    spotcategory_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        db_index=True,
        null=True,      # TEMP
        blank=True      # TEMP
    )

    # Category Info
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)

    # Auth tracking
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='spotcategories_created'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='spotcategories_updated'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]

    def save(self, *args, **kwargs):
        if not self.spotcategory_id:
            while True:
                candidate = generate_ulid_with_prefix("cat")
                if not SpotCategory.objects.filter(spotcategory_id=candidate).exists():
                    self.spotcategory_id = candidate
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
