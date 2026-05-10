from django.db import models

from life_hub.utils import generate_ulid_with_prefix

from portfoliohub.models.profile_snapshot import ProfileSnapshot


class ProfileHobby(models.Model):
    id = models.BigAutoField(primary_key=True)

    profilehobby_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        editable=False
    )

    profile_snapshot = models.ForeignKey(
        ProfileSnapshot,
        on_delete=models.CASCADE,
        related_name="hobbies"
    )

    hobby_name = models.CharField(max_length=255)

    position = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["position", "hobby_name"]

    def save(self, *args, **kwargs):

        if not self.profilehobby_id:
            while True:
                candidate = generate_ulid_with_prefix("hby")

                if not ProfileHobby.objects.filter(
                    profilehobby_id=candidate
                ).exists():
                    self.profilehobby_id = candidate
                    break

        super().save(*args, **kwargs)

    def __str__(self):
        return self.hobby_name
