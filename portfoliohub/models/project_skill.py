from django.db import models

from portfoliohub.models.profile_project import ProfileProject
from portfoliohub.models.master_skill import MasterSkill


class ProjectSkill(models.Model):
    id = models.BigAutoField(primary_key=True)

    project = models.ForeignKey(
        ProfileProject,
        on_delete=models.CASCADE,
        related_name="project_skills"
    )

    skill = models.ForeignKey(
        MasterSkill,
        on_delete=models.CASCADE,
        related_name="skill_projects"
    )

    class Meta:
        unique_together = ["project", "skill"]

    def __str__(self):
        return f"{self.project.project_name} → {self.skill.name}"
