# portfoliohub/models/resume_project.py

from django.db import models
from django.conf import settings
from django.utils.text import slugify

from life_hub.utils import generate_ulid_with_prefix

from portfoliohub.models.profile_snapshot import ProfileSnapshot
from portfoliohub.models.resume_template import ResumeTemplate


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

    resume_template = models.ForeignKey(
        ResumeTemplate,
        on_delete=models.PROTECT,
        related_name="resume_projects",
        null=True,
        blank=True,
    )

    title = models.CharField(max_length=255)

    slug = models.SlugField(
        max_length=255,
        unique=True
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

    is_public = models.BooleanField(default=False)

    is_pdf_generated = models.BooleanField(default=False)

    pdf_public_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    @staticmethod
    def generate_unique_slug(title, exclude_id=None):

        base_slug = slugify(title)

        slug = base_slug
        counter = 1

        queryset = ResumeProject.objects.all()

        if exclude_id:
            queryset = queryset.exclude(id=exclude_id)

        while queryset.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug

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
            self.slug = self.generate_unique_slug(
                self.title
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
