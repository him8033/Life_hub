from django.urls import path
from portfoliohub.views.profile_snapshot import (
    ProfileSnapshotAPIView,
    ProfileSnapshotDetailAPIView,
    ProfileSnapshotDuplicateAPIView
)
from portfoliohub.views.profile_basic_info import (
    ProfileBasicInfoAPIView
)
from portfoliohub.views.profile_social_link import (
    ProfileSocialLinkAPIView,
    ProfileSocialLinkDetailAPIView,
    ProfileSocialLinkReorderAPIView
)
from portfoliohub.views.profile_education import (
    ProfileEducationAPIView,
    ProfileEducationDetailAPIView,
    ProfileEducationReorderAPIView
)
from portfoliohub.views.profile_experience import (
    ProfileExperienceAPIView,
    ProfileExperienceDetailAPIView,
    ProfileExperienceReorderAPIView
)
from portfoliohub.views.skill_category import (
    SkillCategoryListAPIView,
    SkillCategoryCreateAPIView,
    SkillCategoryDetailAPIView
)
from portfoliohub.views.master_skill import (
    MasterSkillAPIView,
    MasterSkillDetailAPIView
)
from portfoliohub.views.profile_skill import (
    ProfileSkillAPIView,
    ProfileSkillDetailAPIView,
    ProfileSkillReorderAPIView
)
from portfoliohub.views.profile_project import (
    ProfileProjectAPIView,
    ProfileProjectDetailAPIView,
    ProfileProjectReorderAPIView,
)
from portfoliohub.views.project_skill import (
    ProjectSkillAPIView,
    ProjectSkillDeleteAPIView,
)

urlpatterns = [
    #  Skill Category Routes
    path("skill-categories/", SkillCategoryListAPIView.as_view()),
    # ADMIN
    path("skill-categories/create/", SkillCategoryCreateAPIView.as_view()),
    path("skill-categories/<str:category_id>/",
         SkillCategoryDetailAPIView.as_view()),

    # Master Skills Routes
    path("master-skills/", MasterSkillAPIView.as_view()),
    path("master-skills/<str:skill_id>/", MasterSkillDetailAPIView.as_view()),

    # Snapshot Routes
    path("", ProfileSnapshotAPIView.as_view()),
    path("<str:snapshot_id>/",
         ProfileSnapshotDetailAPIView.as_view()),
    path("<str:snapshot_id>/duplicate/",
         ProfileSnapshotDuplicateAPIView.as_view()),

    # Profile Basic Info Route
    path("<str:snapshot_id>/basic-info/",
         ProfileBasicInfoAPIView.as_view()),

    # Profile Social Link Routes
    path("<str:snapshot_id>/social-links/",
         ProfileSocialLinkAPIView.as_view()),
    path("social-links/<str:link_id>/", ProfileSocialLinkDetailAPIView.as_view()),
    path("<str:snapshot_id>/social-links/reorder/",
         ProfileSocialLinkReorderAPIView.as_view()),

    #  Profile Education Routes
    path("<str:snapshot_id>/educations/", ProfileEducationAPIView.as_view()),
    path("educations/<str:edu_id>/", ProfileEducationDetailAPIView.as_view()),
    path("<str:snapshot_id>/educations/reorder/",
         ProfileEducationReorderAPIView.as_view()),

    #  Profile Experience Routes
    path("<str:snapshot_id>/experiences/", ProfileExperienceAPIView.as_view()),
    path("experiences/<str:exp_id>/", ProfileExperienceDetailAPIView.as_view()),
    path("<str:snapshot_id>/experiences/reorder/",
         ProfileExperienceReorderAPIView.as_view()),

    # Profile Skills Routes
    path("<str:snapshot_id>/skills/", ProfileSkillAPIView.as_view()),
    path("skills/<str:skill_id>/", ProfileSkillDetailAPIView.as_view()),
    path("<str:snapshot_id>/skills/reorder/",
         ProfileSkillReorderAPIView.as_view()),

    # Profile Projects Routes
    path("<str:snapshot_id>/projects/", ProfileProjectAPIView.as_view()),
    path("projects/<str:project_id>/", ProfileProjectDetailAPIView.as_view()),
    path("<str:snapshot_id>/projects/reorder/",
         ProfileProjectReorderAPIView.as_view()),

    # Profile Project Skill Mapping Routes
    path("projects/<str:project_id>/skills/", ProjectSkillAPIView.as_view()),
    path("projects/<str:project_id>/skills/<str:skill_id>/",
         ProjectSkillDeleteAPIView.as_view()),
]
