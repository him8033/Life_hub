from django.db import models
from django.conf import settings

from life_hub.utils import generate_ulid_with_prefix

from portfoliohub.models.profile_snapshot import ProfileSnapshot


class PortfolioProject(models.Model):

    id = models.BigAutoField(primary_key=True)

    portfolio_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        editable=False
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="portfolio_projects"
    )

    profile_snapshot = models.ForeignKey(
        ProfileSnapshot,
        on_delete=models.CASCADE,
        related_name="portfolio_projects"
    )

    # BASIC
    title = models.CharField(max_length=255)

    slug = models.SlugField(
        unique=True,
        db_index=True
    )

    # THEME
    theme_key = models.CharField(
        max_length=100,
        default="developer_dark"
    )

    # DOMAIN
    custom_domain = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    # SEO
    seo_title = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    seo_description = models.TextField(
        blank=True,
        null=True
    )

    # HERO SECTION
    hero_title = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    hero_subtitle = models.TextField(
        blank=True,
        null=True
    )

    # CONTROL
    is_public = models.BooleanField(default=False)

    # ANALYTICS
    view_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ============================================
    # SAVE
    # ============================================

    def save(self, *args, **kwargs):

        if not self.portfolio_id:

            while True:

                candidate = generate_ulid_with_prefix("port")

                if not PortfolioProject.objects.filter(
                    portfolio_id=candidate
                ).exists():

                    self.portfolio_id = candidate
                    break

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
