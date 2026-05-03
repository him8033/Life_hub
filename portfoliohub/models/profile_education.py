from django.db import models
from life_hub.utils import generate_ulid_with_prefix

from portfoliohub.models.profile_snapshot import ProfileSnapshot


class ProfileEducation(models.Model):
    id = models.BigAutoField(primary_key=True)

    profileeducation_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        editable=False
    )

    profile_snapshot = models.ForeignKey(
        ProfileSnapshot,
        on_delete=models.CASCADE,
        related_name="educations"
    )

    degree_name = models.CharField(max_length=255)
    institution_name = models.CharField(max_length=255)

    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False)

    score = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    full_address = models.TextField(blank=True, null=True)

    position = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.profileeducation_id:
            while True:
                candidate = generate_ulid_with_prefix("edu")
                if not ProfileEducation.objects.filter(profileeducation_id=candidate).exists():
                    self.profileeducation_id = candidate
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.degree_name} - {self.institution_name}"
