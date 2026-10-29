from django.db import models
from django.conf import settings
from life_hub.utils import generate_ulid_with_prefix


class UserRole(models.Model):
    """
    Many-to-many relationship between User and Role.
    Supports audit information and future temporary roles.
    """
    id = models.BigAutoField(primary_key=True)
    
    userrole_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        editable=False
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_roles',
        db_index=True
    )
    
    role = models.ForeignKey(
        'account.Role',
        on_delete=models.CASCADE,
        related_name='user_roles',
        db_index=True
    )
    
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_roles',
        help_text="User who assigned this role"
    )
    
    assigned_at = models.DateTimeField(auto_now_add=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'account_userrole'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'role'],
                name='unique_user_role'
            )
        ]
        indexes = [
            models.Index(fields=['userrole_id']),
            models.Index(fields=['user']),
            models.Index(fields=['role']),
        ]
        ordering = ['-assigned_at']
    
    def save(self, *args, **kwargs):
        if not self.userrole_id:
            while True:
                candidate = generate_ulid_with_prefix("ur")
                if not UserRole.objects.filter(userrole_id=candidate).exists():
                    self.userrole_id = candidate
                    break
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.email} - {self.role.name}"