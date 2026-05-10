# portfoliohub/models/resume_project.py

from django.db import models
from django.conf import settings
from django.utils.text import slugify
from cloudinary.models import CloudinaryField

from life_hub.utils import generate_ulid_with_prefix
from portfoliohub.models.profile_snapshot import ProfileSnapshot


class ResumeProject(models.Model):
    id = models.BigAutoField(primary_key=True)

    resume_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        editable=False
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="resume_projects"
    )

    profile_snapshot = models.ForeignKey(
        ProfileSnapshot,
        on_delete=models.CASCADE,
        related_name="resume_projects"
    )

    title = models.CharField(max_length=255)

    slug = models.SlugField(
        max_length=255,
        unique=True
    )

    # PRESENTATION
    template_key = models.CharField(
        max_length=100,
        default="modern_ats"
    )

    font_family = models.CharField(
        max_length=100,
        default="Poppins"
    )

    primary_color = models.CharField(
        max_length=20,
        default="#2563EB"
    )

    layout = models.CharField(
        max_length=100,
        default="single_column"
    )

    # CONTROL
    is_public = models.BooleanField(default=False)

    # PDF
    is_pdf_generated = models.BooleanField(default=False)

    last_generated_pdf = CloudinaryField(
        resource_type="raw",
        blank=True,
        null=True
    )

    pdf_public_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    # ============================================
    # AUTO SAVE
    # ============================================

    def save(self, *args, **kwargs):

        if not self.resume_id:

            while True:
                candidate = generate_ulid_with_prefix("res")

                if not ResumeProject.objects.filter(
                    resume_id=candidate
                ).exists():

                    self.resume_id = candidate
                    break

        if not self.slug:

            base_slug = slugify(self.title)

            slug = base_slug
            counter = 1

            while ResumeProject.objects.filter(
                slug=slug
            ).exists():

                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
