from django.db import models
from django.conf import settings
from django.utils import timezone
from life_hub.utils import generate_ulid_with_prefix
import hashlib
import secrets


class OTP(models.Model):
    """
    OTP records with security metadata.
    OTP codes are hashed before storage for security.
    """
    id = models.BigAutoField(primary_key=True)
    
    otp_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        editable=False
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='otps',
        db_index=True
    )
    
    purpose = models.ForeignKey(
        'account.OTPPurpose',
        on_delete=models.CASCADE,
        related_name='otps',
        db_index=True
    )
    
    code_hash = models.CharField(
        max_length=255,
        db_index=True,
        help_text="SHA-256 hash of the OTP code"
    )
    
    attempts = models.IntegerField(default=0, help_text="Number of verification attempts")
    is_used = models.BooleanField(default=False, db_index=True)
    
    expires_at = models.DateTimeField(db_index=True)
    used_at = models.DateTimeField(null=True, blank=True)
    
    # Security metadata
    requested_ip = models.CharField(max_length=45, blank=True, null=True, help_text="IP address of request")
    requested_user_agent = models.TextField(blank=True, null=True, help_text="User agent of request")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'account_otp'
        indexes = [
            models.Index(fields=['otp_id']),
            models.Index(fields=['user']),
            models.Index(fields=['purpose']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['is_used']),
        ]
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.otp_id:
            while True:
                candidate = generate_ulid_with_prefix("otpr")
                if not OTP.objects.filter(otp_id=candidate).exists():
                    self.otp_id = candidate
                    break
        super().save(*args, **kwargs)
    
    @classmethod
    def generate_code(cls, length=6):
        """Generate a secure random OTP code."""
        return ''.join(secrets.choice('0123456789') for _ in range(length))
    
    @classmethod
    def hash_code(cls, code):
        """Hash OTP code using SHA-256."""
        return hashlib.sha256(code.encode()).hexdigest()
    
    def verify_code(self, code):
        """Verify if the provided code matches the stored hash."""
        return self.code_hash == self.hash_code(code)
    
    def is_expired(self):
        """Check if OTP has expired."""
        return timezone.now() > self.expires_at
    
    def can_attempt(self):
        """Check if user can still attempt verification."""
        return self.attempts < self.purpose.max_attempts and not self.is_used and not self.is_expired()
    
    def __str__(self):
        return f"OTP for {self.user.email} - {self.purpose.name}"