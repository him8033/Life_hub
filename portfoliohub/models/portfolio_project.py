from django.db import models
from django.conf import settings
from django.utils.text import slugify

from life_hub.utils import generate_ulid_with_prefix

from portfoliohub.models.profile_snapshot import ProfileSnapshot
from portfoliohub.models.portfolio_theme import PortfolioTheme


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

    portfolio_theme = models.ForeignKey(
        PortfolioTheme,
        on_delete=models.PROTECT,
        related_name="portfolio_projects",
        null=True,
        blank=True,
    )

    # BASIC
    title = models.CharField(max_length=255)

    slug = models.SlugField(
        unique=True,
        db_index=True
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

    @staticmethod
    def generate_unique_slug(title, exclude_id=None):

        base_slug = slugify(title)

        slug = base_slug
        counter = 1

        queryset = PortfolioProject.objects.all()

        if exclude_id:
            queryset = queryset.exclude(id=exclude_id)

        while queryset.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug

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

        if not self.slug:
            self.slug = self.generate_unique_slug(
                self.title
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
