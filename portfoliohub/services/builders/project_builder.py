# portfoliohub/services/builders/project_builder.py

from django.db.models import Prefetch

from portfoliohub.models.project_image import (
    ProjectImage
)

from portfoliohub.models.project_skill import (
    ProjectSkill
)

from portfoliohub.services.builder_utils import (
    BuilderUtils
)


class ProjectBuilder:

    @staticmethod
    def build(snapshot):

        project_queryset = (
            snapshot.projects
            .prefetch_related(
                Prefetch(
                    "images",
                    queryset=ProjectImage.objects.order_by(
                        "position"
                    )
                ),
                Prefetch(
                    "project_skills",
                    queryset=(
                        ProjectSkill.objects
                        .select_related("skill")
                    )
                )
            )
            .order_by(
                "position",
                "priority",
                "-is_featured"
            )
        )

        projects = []

        for project in project_queryset:

            projects.append({

                "profileproject_id":
                    project.profileproject_id,

                "project_name":
                    project.project_name,

                "short_description":
                    project.short_description,

                "full_description":
                    project.full_description,

                "code_url":
                    project.code_url,

                "live_url":
                    project.live_url,

                "is_live":
                    project.is_live,

                "is_featured":
                    project.is_featured,

                "thumbnail":
                    BuilderUtils.get_file_url(
                        project.thumbnail
                    ),

                "priority":
                    project.priority,

                "position":
                    project.position,

                "skills": [
                    {
                        "name":
                            ps.skill.name,

                        "slug":
                            ps.skill.slug,
                    }
                    for ps in project.project_skills.all()
                        ],

                "images": [
                    {
                        "projectimage_id":
                            image.projectimage_id,

                        "image":
                            BuilderUtils.get_file_url(
                                image.image
                            ),

                        "caption":
                            image.caption,

                        "is_primary":
                            image.is_primary,

                        "position":
                            image.position,
                    }
                    for image in project.images.all()
                        ],
            })

        return projects
