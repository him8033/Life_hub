from django.db import models
from cloudinary.models import CloudinaryField

from life_hub.utils import generate_ulid_with_prefix

from portfoliohub.models.profile_project import ProfileProject


class ProjectImage(models.Model):
    id = models.BigAutoField(primary_key=True)

    projectimage_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        editable=False
    )

    project = models.ForeignKey(
        ProfileProject,
        on_delete=models.CASCADE,
        related_name="images"
    )

    image = CloudinaryField(
        "image",
        blank=True,
        null=True
    )

    public_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    caption = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    is_primary = models.BooleanField(default=False)

    position = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    # ============================================
    # SAVE
    # ============================================

    def save(self, *args, **kwargs):

        if not self.projectimage_id:

            while True:

                candidate = generate_ulid_with_prefix("pimg")

                if not ProjectImage.objects.filter(
                    projectimage_id=candidate
                ).exists():

                    self.projectimage_id = candidate
                    break

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.project.project_name} Image"
