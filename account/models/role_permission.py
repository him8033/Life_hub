from django.db import models
from life_hub.utils import generate_ulid_with_prefix


class RolePermission(models.Model):
    """
    Many-to-many relationship between Role and Permission.
    Defines which permissions each role has.
    """
    id = models.BigAutoField(primary_key=True)
    
    rolepermission_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        editable=False
    )
    
    role = models.ForeignKey(
        'account.Role',
        on_delete=models.CASCADE,
        related_name='role_permissions',
        db_index=True
    )
    
    permission = models.ForeignKey(
        'account.Permission',
        on_delete=models.CASCADE,
        related_name='role_permissions',
        db_index=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'account_rolepermission'
        constraints = [
            models.UniqueConstraint(
                fields=['role', 'permission'],
                name='unique_role_permission'
            )
        ]
        indexes = [
            models.Index(fields=['rolepermission_id']),
            models.Index(fields=['role']),
            models.Index(fields=['permission']),
        ]
        ordering = ['role', 'permission']
    
    def save(self, *args, **kwargs):
        if not self.rolepermission_id:
            while True:
                candidate = generate_ulid_with_prefix("rp")
                if not RolePermission.objects.filter(rolepermission_id=candidate).exists():
                    self.rolepermission_id = candidate
                    break
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.role.name} - {self.permission.slug}"