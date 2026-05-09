from django.db import models
from life_hub.utils import generate_ulid_with_prefix


class SkillCategory(models.Model):
    id = models.BigAutoField(primary_key=True)

    skillcategory_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        editable=False
    )

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    icon = models.CharField(max_length=100, blank=True, null=True)

    position = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.skillcategory_id:
            while True:
                candidate = generate_ulid_with_prefix("cat")
                if not SkillCategory.objects.filter(skillcategory_id=candidate).exists():
                    self.skillcategory_id = candidate
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
