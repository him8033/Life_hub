from django.db import models
from life_hub.utils import generate_ulid_with_prefix


class Role(models.Model):
    """
    Dynamic role system for RBAC.
    Replaces hardcoded role choices in User model.
    """
    id = models.BigAutoField(primary_key=True)
    
    role_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        editable=False
    )
    
    name = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=100, unique=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True, db_index=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'account_role'
        indexes = [
            models.Index(fields=['role_id']),
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.role_id:
            while True:
                candidate = generate_ulid_with_prefix("role")
                if not Role.objects.filter(role_id=candidate).exists():
                    self.role_id = candidate
                    break
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name