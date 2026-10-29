"""
Password Reset Token Model
Stores single-use tokens for password reset flow
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from life_hub.utils import generate_ulid_with_prefix


class PasswordResetToken(models.Model):
    """
    Model for storing single-use password reset tokens.
    Tokens are invalidated after use or expiration.
    """
    id = models.BigAutoField(primary_key=True)
    
    token_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        editable=False
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='password_reset_tokens',
        db_index=True
    )
    
    email = models.EmailField(
        help_text="Email address associated with the token"
    )
    
    token = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text="Secure random token"
    )
    
    token_type = models.CharField(
        max_length=20,
        choices=[
            ('request', 'Password Reset Request'),
            ('confirm', 'Password Reset Confirm'),
        ],
        db_index=True,
        help_text="Type of token"
    )
    
    is_used = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Whether the token has been used"
    )
    
    used_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when token was used"
    )
    
    expires_at = models.DateTimeField(
        db_index=True,
        help_text="Token expiration time"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'account_passwordresettoken'
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['user']),
            models.Index(fields=['token_type']),
            models.Index(fields=['is_used']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['token', 'token_type', 'is_used']),
        ]
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.token_id:
            while True:
                candidate = generate_ulid_with_prefix("prt")
                if not PasswordResetToken.objects.filter(token_id=candidate).exists():
                    self.token_id = candidate
                    break
        super().save(*args, **kwargs)
    
    def is_expired(self):
        """Check if token has expired."""
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        """Check if token is valid (not used and not expired)."""
        return not self.is_used and not self.is_expired()
    
    def __str__(self):
        return f"PasswordResetToken for {self.email} ({self.token_type})"
