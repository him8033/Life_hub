from django.db import models

from cloudinary.models import CloudinaryField

from life_hub.utils import generate_ulid_with_prefix

from portfoliohub.models.profile_snapshot import ProfileSnapshot


class ProfileProject(models.Model):
    id = models.BigAutoField(primary_key=True)

    profileproject_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        editable=False
    )

    profile_snapshot = models.ForeignKey(
        ProfileSnapshot,
        on_delete=models.CASCADE,
        related_name="projects"
    )

    project_name = models.CharField(max_length=255)

    short_description = models.TextField()

    full_description = models.TextField(
        blank=True,
        null=True
    )

    code_url = models.URLField(
        blank=True,
        null=True
    )

    live_url = models.URLField(
        blank=True,
        null=True
    )

    # THUMBNAIL
    thumbnail = CloudinaryField(
        "image",
        blank=True,
        null=True
    )

    public_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    is_live = models.BooleanField(default=False)

    is_featured = models.BooleanField(default=False)

    priority = models.IntegerField(default=0)

    position = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):

        if not self.profileproject_id:

            while True:

                candidate = generate_ulid_with_prefix("prj")

                if not ProfileProject.objects.filter(
                    profileproject_id=candidate
                ).exists():

                    self.profileproject_id = candidate
                    break

        super().save(*args, **kwargs)

    def __str__(self):
        return self.project_name
