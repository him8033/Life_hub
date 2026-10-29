from django.db import models
from life_hub.utils import generate_ulid_with_prefix


class UserStatus(models.Model):
    """
    Dynamic user status system.
    Replaces hardcoded status choices and enables business-driven status management.
    """
    id = models.BigAutoField(primary_key=True)
    
    userstatus_id = models.CharField(
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
        db_table = 'account_userstatus'
        indexes = [
            models.Index(fields=['userstatus_id']),
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.userstatus_id:
            while True:
                candidate = generate_ulid_with_prefix("ust")
                if not UserStatus.objects.filter(userstatus_id=candidate).exists():
                    self.userstatus_id = candidate
                    break
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name