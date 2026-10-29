from django.db import models
from django.conf import settings
from life_hub.utils import generate_ulid_with_prefix


class LoginHistory(models.Model):
    """
    Login history tracking for security auditing.
    Records both successful and failed authentication attempts.
    """
    id = models.BigAutoField(primary_key=True)
    
    loginhistory_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        editable=False
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='login_history',
        db_index=True,
        help_text="User who attempted login (null if user not found)"
    )
    
    # Authentication method
    login_method = models.CharField(
        max_length=50,
        db_index=True,
        help_text="Method used for login (email_password, google, github, etc.)"
    )
    
    success = models.BooleanField(db_index=True, help_text="Whether login was successful")
    
    # Request metadata
    ip_address = models.CharField(
        max_length=45,
        blank=True,
        null=True,
        db_index=True,
        help_text="IP address of the login attempt"
    )
    user_agent = models.TextField(
        blank=True,
        null=True,
        help_text="User agent string"
    )
    
    # Device information
    device = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Device type"
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
    
    # Failure information
    failure_reason = models.TextField(
        blank=True,
        null=True,
        help_text="Reason for login failure"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'account_loginhistory'
        indexes = [
            models.Index(fields=['loginhistory_id']),
            models.Index(fields=['user']),
            models.Index(fields=['login_method']),
            models.Index(fields=['success']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.loginhistory_id:
            while True:
                candidate = generate_ulid_with_prefix("lh")
                if not LoginHistory.objects.filter(loginhistory_id=candidate).exists():
                    self.loginhistory_id = candidate
                    break
        super().save(*args, **kwargs)
    
    def __str__(self):
        user_info = self.user.email if self.user else "Unknown user"
        status = "Success" if self.success else f"Failed: {self.failure_reason}"
        return f"{user_info} - {self.login_method} - {status}"