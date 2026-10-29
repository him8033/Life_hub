from django.db import models
from life_hub.utils import generate_ulid_with_prefix


class OTPPurpose(models.Model):
    """
    OTP purpose configuration.
    Each purpose can have different expiry time, max attempts, and resend cooldown.
    """
    id = models.BigAutoField(primary_key=True)
    
    otppurpose_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        editable=False
    )
    
    name = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=100, unique=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    
    # OTP configuration
    expiry_seconds = models.IntegerField(
        default=300,
        help_text="OTP expiry time in seconds"
    )
    max_attempts = models.IntegerField(
        default=3,
        help_text="Maximum verification attempts"
    )
    resend_cooldown_seconds = models.IntegerField(
        default=60,
        help_text="Cooldown between resend requests in seconds"
    )
    
    is_active = models.BooleanField(default=True, db_index=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'account_otppurpose'
        indexes = [
            models.Index(fields=['otppurpose_id']),
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.otppurpose_id:
            while True:
                candidate = generate_ulid_with_prefix("otp")
                if not OTPPurpose.objects.filter(otppurpose_id=candidate).exists():
                    self.otppurpose_id = candidate
                    break
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name