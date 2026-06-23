# portfoliohub/services/duplicate_modules/project_duplicate.py

from portfoliohub.models.profile_project import (
    ProfileProject
)
from portfoliohub.models.project_skill import (
    ProjectSkill
)
from portfoliohub.models.project_image import (
    ProjectImage
)
from life_hub.utils import generate_ulid_with_prefix


class ProjectDuplicate:

    @staticmethod
    def copy(source_snapshot, new_snapshot):

        projects = (
            source_snapshot.projects
            .prefetch_related(
                "project_skills__skill",
                "images"
            )
            .all()
        )

        for project in projects:

            new_project = ProfileProject.objects.create(
                profileproject_id=generate_ulid_with_prefix("prj"),
                profile_snapshot=new_snapshot,
                project_name=project.project_name,
                short_description=project.short_description,
                full_description=project.full_description,
                code_url=project.code_url,
                live_url=project.live_url,
                is_live=project.is_live,
                is_featured=project.is_featured,
                thumbnail=project.thumbnail,
                public_id=project.public_id,
                priority=project.priority,
                position=project.position,
            )

            # ==========================
            # PROJECT SKILLS
            # ==========================

            ProjectSkill.objects.bulk_create([
                ProjectSkill(
                    project=new_project,
                    skill=item.skill,
                )
                for item in project.project_skills.all()
            ])

            # ==========================
            # PROJECT IMAGES
            # ==========================

            ProjectImage.objects.bulk_create([
                ProjectImage(
                    projectimage_id=generate_ulid_with_prefix("pimg"),
                    project=new_project,
                    image=image.image,
                    public_id=image.public_id,
                    caption=image.caption,
                    is_primary=image.is_primary,
                    position=image.position,
                )
                for image in project.images.all()
            ])
