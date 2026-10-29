from django.db import models
from django.conf import settings
from django.utils import timezone
from life_hub.utils import generate_ulid_with_prefix


class UserSession(models.Model):
    """
    User session management for multi-device support.
    Tracks active sessions and supports revocation.
    """
    id = models.BigAutoField(primary_key=True)
    
    usersession_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        editable=False
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sessions',
        db_index=True
    )
    
    # Session identification
    session_identifier = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text="Unique session identifier"
    )
    
    refresh_token_hash = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Hash of the refresh token for validation"
    )
    
    # Device information
    device = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Device type (desktop, mobile, tablet)"
    )
    browser = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Browser name"
    )
    operating_system = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Operating system"
    )
    
    # Security metadata
    ip_address = models.CharField(
        max_length=45,
        blank=True,
        null=True,
        db_index=True,
        help_text="IP address of the session"
    )
    user_agent = models.TextField(
        blank=True,
        null=True,
        help_text="User agent string"
    )
    
    is_active = models.BooleanField(default=True, db_index=True)
    
    # Activity tracking
    last_activity_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(db_index=True)
    
    # Revocation tracking
    revoked_at = models.DateTimeField(null=True, blank=True)
    revoked_reason = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Reason for session revocation"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'account_usersession'
        indexes = [
            models.Index(fields=['usersession_id']),
            models.Index(fields=['user']),
            models.Index(fields=['session_identifier']),
            models.Index(fields=['is_active']),
            models.Index(fields=['expires_at']),
        ]
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.usersession_id:
            while True:
                candidate = generate_ulid_with_prefix("uss")
                if not UserSession.objects.filter(usersession_id=candidate).exists():
                    self.usersession_id = candidate
                    break
        super().save(*args, **kwargs)
    
    @classmethod
    def hash_refresh_token(cls, refresh_token):
        """Hash refresh token for secure storage."""
        import hashlib
        return hashlib.sha256(refresh_token.encode()).hexdigest()
    
    def is_expired(self):
        """Check if session has expired."""
        return timezone.now() > self.expires_at
    
    def is_revoked(self):
        """Check if session has been revoked."""
        return self.revoked_at is not None
    
    def revoke(self, reason=None):
        """Revoke the session."""
        self.is_active = False
        self.revoked_at = timezone.now()
        self.revoked_reason = reason
        self.save(update_fields=['is_active', 'revoked_at', 'revoked_reason'])
    
    def update_activity(self):
        """Update last activity timestamp."""
        self.last_activity_at = timezone.now()
        self.save(update_fields=['last_activity_at'])
    
    def __str__(self):
        return f"Session for {self.user.email} - {self.device or 'Unknown'}"