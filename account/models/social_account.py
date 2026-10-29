from django.db import models
from django.conf import settings
from life_hub.utils import generate_ulid_with_prefix


class SocialAccount(models.Model):
    """
    User social account links for OAuth providers.
    Supports multiple social accounts per user across different providers.
    """
    id = models.BigAutoField(primary_key=True)
    
    socialaccount_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        editable=False
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='social_accounts',
        db_index=True
    )
    
    provider = models.ForeignKey(
        'account.SocialProvider',
        on_delete=models.CASCADE,
        related_name='social_accounts',
        db_index=True
    )
    
    # Provider identity
    provider_user_id = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Unique user ID from the provider"
    )
    provider_email = models.EmailField(
        blank=True,
        null=True,
        help_text="Email from the provider (may be unverified)"
    )
    provider_username = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Username from the provider"
    )
    avatar_url = models.URLField(
        blank=True,
        null=True,
        help_text="Avatar URL from the provider"
    )
    
    # Additional provider metadata
    provider_metadata = models.JSONField(
        blank=True,
        null=True,
        help_text="Additional data from the provider"
    )
    
    linked_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'account_socialaccount'
        constraints = [
            models.UniqueConstraint(
                fields=['provider', 'provider_user_id'],
                name='unique_provider_identity'
            )
        ]
        indexes = [
            models.Index(fields=['socialaccount_id']),
            models.Index(fields=['user']),
            models.Index(fields=['provider']),
            models.Index(fields=['provider_user_id']),
        ]
        ordering = ['-linked_at']
    
    def save(self, *args, **kwargs):
        if not self.socialaccount_id:
            while True:
                candidate = generate_ulid_with_prefix("sa")
                if not SocialAccount.objects.filter(socialaccount_id=candidate).exists():
                    self.socialaccount_id = candidate
                    break
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.email} - {self.provider.name}"