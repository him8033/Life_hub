from django.db import models
from life_hub.utils import generate_ulid_with_prefix
from django.utils.text import slugify


class MasterLanguage(models.Model):
    id = models.BigAutoField(primary_key=True)

    masterlanguage_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        editable=False
    )

    name = models.CharField(max_length=100, unique=True)

    slug = models.SlugField(
        max_length=120,
        unique=True,
        blank=True
    )

    code = models.CharField(
        max_length=10,
        blank=True,
        null=True
    )

    icon = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    position = models.IntegerField(default=0)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["position", "name"]

    def save(self, *args, **kwargs):

        # GENERATE ID
        if not self.masterlanguage_id:
            while True:
                candidate = generate_ulid_with_prefix("lng")

                if not MasterLanguage.objects.filter(
                    masterlanguage_id=candidate
                ).exists():
                    self.masterlanguage_id = candidate
                    break

        # GENERATE SLUG
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
