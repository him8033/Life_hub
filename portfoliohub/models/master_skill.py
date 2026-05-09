from django.db import models
from cloudinary.models import CloudinaryField

from life_hub.utils import generate_ulid_with_prefix

from portfoliohub.models.skill_category import SkillCategory


class MasterSkill(models.Model):
    id = models.BigAutoField(primary_key=True)

    masterskill_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        editable=False
    )

    category = models.ForeignKey(
        SkillCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name="master_skills"
    )

    name = models.CharField(max_length=255)

    slug = models.SlugField(
        unique=True,
        max_length=255
    )

    icon = models.CharField(
        max_length=255,
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
        null=True,
        editable=False
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    is_active = models.BooleanField(default=True)

    priority = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):

        if not self.masterskill_id:
            while True:
                candidate = generate_ulid_with_prefix("msk")

                if not MasterSkill.objects.filter(
                    masterskill_id=candidate
                ).exists():

                    self.masterskill_id = candidate
                    break

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
