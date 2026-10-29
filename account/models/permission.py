from django.db import models
from life_hub.utils import generate_ulid_with_prefix


class Permission(models.Model):
    """
    Dynamic permission system for granular access control.
    Permissions are assigned to roles, which are then assigned to users.
    """
    id = models.BigAutoField(primary_key=True)
    
    permission_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        editable=False
    )
    
    name = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=100, unique=True, db_index=True)
    module = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True, db_index=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'account_permission'
        indexes = [
            models.Index(fields=['permission_id']),
            models.Index(fields=['slug']),
            models.Index(fields=['module']),
            models.Index(fields=['is_active']),
        ]
        ordering = ['module', 'name']
    
    def save(self, *args, **kwargs):
        if not self.permission_id:
            while True:
                candidate = generate_ulid_with_prefix("perm")
                if not Permission.objects.filter(permission_id=candidate).exists():
                    self.permission_id = candidate
                    break
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.module}.{self.slug}" if self.module else self.slug