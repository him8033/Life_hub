from django.db import models
from cloudinary.models import CloudinaryField

from portfoliohub.models.resume_project import ResumeProject


class ResumeExport(models.Model):
    id = models.BigAutoField(primary_key=True)

    resume = models.ForeignKey(
        ResumeProject,
        on_delete=models.CASCADE,
        related_name="exports"
    )

    # CLOUDINARY FILE
    exported_file = CloudinaryField(
        resource_type="raw",
        blank=True,
        null=True
    )

    public_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    export_type = models.CharField(
        max_length=50,
        choices=[
            ("pdf", "PDF"),
            ("docx", "DOCX"),
            ("txt", "TXT"),
        ],
        default="pdf"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.resume.title} - {self.export_type}"
