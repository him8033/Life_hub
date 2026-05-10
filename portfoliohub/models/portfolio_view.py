from django.db import models

from portfoliohub.models.portfolio_project import PortfolioProject


class PortfolioView(models.Model):
    id = models.BigAutoField(primary_key=True)

    portfolio = models.ForeignKey(
        PortfolioProject,
        on_delete=models.CASCADE,
        related_name="views"
    )

    ip_address = models.CharField(max_length=255)

    country = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    viewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.portfolio.title} - {self.ip_address}"
