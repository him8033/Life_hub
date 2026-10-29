from django.db import models
from life_hub.utils import generate_ulid_with_prefix


class SocialProvider(models.Model):
    """
    Social provider configuration.
    Database-driven provider management for OAuth authentication.
    """
    id = models.BigAutoField(primary_key=True)
    
    socialprovider_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        editable=False
    )
    
    name = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=100, unique=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    
    is_active = models.BooleanField(default=True, db_index=True)
    
    # Provider configuration metadata (JSON field for flexibility)
    provider_metadata = models.JSONField(
        blank=True,
        null=True,
        help_text="Provider-specific configuration (stored securely, not exposed via API)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'account_socialprovider'
        indexes = [
            models.Index(fields=['socialprovider_id']),
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.socialprovider_id:
            while True:
                candidate = generate_ulid_with_prefix("sp")
                if not SocialProvider.objects.filter(socialprovider_id=candidate).exists():
                    self.socialprovider_id = candidate
                    break
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name