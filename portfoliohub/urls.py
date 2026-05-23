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
    PublicSkillCategoryListAPIView,
    SkillCategoryListAPIView,
    SkillCategoryCreateAPIView,
    SkillCategoryDetailAPIView,
)
from portfoliohub.views.master_skill import (
    PublicMasterSkillListAPIView,
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
from portfoliohub.views.project_image import (
    ProjectImageAPIView,
    ProjectImageDetailAPIView,
    ProjectImageReorderAPIView,
)
from portfoliohub.views.profile_certificate import (
    ProfileCertificateAPIView,
    ProfileCertificateDetailAPIView,
    ProfileCertificateReorderAPIView,
)
from portfoliohub.views.profile_achievement import (
    ProfileAchievementAPIView,
    ProfileAchievementDetailAPIView,
    ProfileAchievementReorderAPIView,
)
from portfoliohub.views.master_language import (
    PublicMasterLanguageListAPIView,
    MasterLanguageAPIView,
    MasterLanguageDetailAPIView,
)
from portfoliohub.views.profile_language import (
    ProfileLanguageAPIView,
    ProfileLanguageDetailAPIView,
    ProfileLanguageReorderAPIView,
)
from portfoliohub.views.profile_hobby import (
    ProfileHobbyAPIView,
    ProfileHobbyDetailAPIView,
    ProfileHobbyReorderAPIView,
)
from portfoliohub.views.profile_strength import (
    ProfileStrengthAPIView,
    ProfileStrengthDetailAPIView,
    ProfileStrengthReorderAPIView,
)
from portfoliohub.views.profile_custom_section import (
    ProfileCustomSectionAPIView,
    ProfileCustomSectionDetailAPIView,
    ProfileCustomSectionReorderAPIView,
)
from portfoliohub.views.resume_project import (
    ResumeProjectAPIView,
    ResumeProjectDetailAPIView,
    ResumeProjectDuplicateAPIView,
    ResumeProjectGeneratePDFAPIView,
    PublicResumeProjectAPIView,
)
from portfoliohub.views.portfolio_project import (
    PortfolioProjectAPIView,
    PortfolioProjectDetailAPIView,
    PortfolioProjectDuplicateAPIView,
    PublicPortfolioProjectAPIView,
)
from portfoliohub.views.resume_template import (
    PublicResumeTemplateAPIView,
    ResumeTemplateAPIView,
    ResumeTemplateDetailAPIView,
)
from portfoliohub.views.portfolio_theme import (
    PublicPortfolioThemeListAPIView,
    PortfolioThemeAPIView,
    PortfolioThemeDetailAPIView,
)
from portfoliohub.views.portfolio_view import (
    PortfolioViewTrackAPIView,
    PortfolioAnalyticsAPIView,
)
from portfoliohub.views.resume_export import (
    ResumeExportAPIView,
    ResumeExportDetailAPIView,
)

urlpatterns = [
    # Resume Routes
    path("resume-projects/", ResumeProjectAPIView.as_view()),
    path("resume-projects/<str:resume_id>/",
         ResumeProjectDetailAPIView.as_view()),
    path("resume-projects/<str:resume_id>/duplicate/",
         ResumeProjectDuplicateAPIView.as_view()),
    path("resume-projects/<str:resume_id>/generate-pdf/",
         ResumeProjectGeneratePDFAPIView.as_view()),
    path("public/resume/<slug:slug>/", PublicResumeProjectAPIView.as_view()),

    # Resume Export Routes
    path("resume-projects/<str:resume_id>/exports/",
         ResumeExportAPIView.as_view()),
    path("resume-exports/<int:export_id>/",
         ResumeExportDetailAPIView.as_view()),

    # Portfolio Routes
    path("portfolio-projects/", PortfolioProjectAPIView.as_view()),
    path("portfolio-projects/<str:portfolio_id>/",
         PortfolioProjectDetailAPIView.as_view()),
    path("portfolio-projects/<str:portfolio_id>/duplicate/",
         PortfolioProjectDuplicateAPIView.as_view()),
    path("public/portfolio/<slug:slug>/",
         PublicPortfolioProjectAPIView.as_view()),

    # Portfolio Analytics Routes
    path("portfolio-projects/<str:portfolio_id>/track-view/",
         PortfolioViewTrackAPIView.as_view()),
    path("portfolio-projects/<str:portfolio_id>/analytics/",
         PortfolioAnalyticsAPIView.as_view()),

    # Resume Template Routes
    # PUBLIC
    path("public/resume-templates/", PublicResumeTemplateAPIView.as_view()),

    # ADMIN
    path("resume-templates/", ResumeTemplateAPIView.as_view()),
    path("resume-templates/<str:template_id>/",
         ResumeTemplateDetailAPIView.as_view()),

    # Portfolio Theme Routes
    # PUBLIC
    path("public/portfolio-themes/", PublicPortfolioThemeListAPIView.as_view()),

    # ADMIN
    path("portfolio-themes/", PortfolioThemeAPIView.as_view()),
    path("portfolio-themes/<str:theme_id>/",
         PortfolioThemeDetailAPIView.as_view()),

    #  Skill Category Routes
    # PUBLIC
    path("public/skill-categories/", PublicSkillCategoryListAPIView.as_view()),

    # ADMIN
    path("skill-categories/", SkillCategoryListAPIView.as_view()),
    path("skill-categories/create/", SkillCategoryCreateAPIView.as_view()),
    path("skill-categories/<str:category_id>/",
         SkillCategoryDetailAPIView.as_view()),

    # Master Skills Routes
    # PUBLIC
    path("public/master-skills/", PublicMasterSkillListAPIView.as_view()),

    # ADMIN
    path("master-skills/", MasterSkillAPIView.as_view()),
    path("master-skills/<str:skill_id>/", MasterSkillDetailAPIView.as_view()),

    # Master Languages Routes
    # PUBLIC
    path("public/master-languages/", PublicMasterLanguageListAPIView.as_view()),

    # ADMIN
    path("master-languages/", MasterLanguageAPIView.as_view()),
    path("master-languages/<str:language_id>/",
         MasterLanguageDetailAPIView.as_view()),

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

    # Profile Project Images Routes
    path("projects/<str:project_id>/images/", ProjectImageAPIView.as_view()),
    path("projects/images/<str:image_id>/",
         ProjectImageDetailAPIView.as_view()),
    path("projects/<str:project_id>/images/reorder/",
         ProjectImageReorderAPIView.as_view()),

    # Profile Certificate Routes
    path("<str:snapshot_id>/certificates/",
         ProfileCertificateAPIView.as_view()),
    path("certificates/<str:certificate_id>/",
         ProfileCertificateDetailAPIView.as_view()),
    path("<str:snapshot_id>/certificates/reorder/",
         ProfileCertificateReorderAPIView.as_view()),

    # Profile Achievements Routes
    path("<str:snapshot_id>/achievements/",
         ProfileAchievementAPIView.as_view()),
    path("achievements/<str:achievement_id>/",
         ProfileAchievementDetailAPIView.as_view()),
    path("<str:snapshot_id>/achievements/reorder/",
         ProfileAchievementReorderAPIView.as_view()),

    # Profile Languages Mapping Routes
    path("<str:snapshot_id>/languages/", ProfileLanguageAPIView.as_view()),
    path("languages/<str:language_mapping_id>/",
         ProfileLanguageDetailAPIView.as_view()),
    path("<str:snapshot_id>/languages/reorder/",
         ProfileLanguageReorderAPIView.as_view()),

    # Profile Hobbies Routes
    path("<str:snapshot_id>/hobbies/", ProfileHobbyAPIView.as_view()),
    path("hobbies/<str:hobby_id>/", ProfileHobbyDetailAPIView.as_view()),
    path("<str:snapshot_id>/hobbies/reorder/",
         ProfileHobbyReorderAPIView.as_view()),

    # Profile Strength Routes
    path("<str:snapshot_id>/strengths/", ProfileStrengthAPIView.as_view()),
    path("strengths/<str:strength_id>/", ProfileStrengthDetailAPIView.as_view()),
    path("<str:snapshot_id>/strengths/reorder/",
         ProfileStrengthReorderAPIView.as_view()),

    # Profile Custom Sections Routes
    path("<str:snapshot_id>/custom-sections/",
         ProfileCustomSectionAPIView.as_view()),
    path("custom-sections/<str:section_id>/",
         ProfileCustomSectionDetailAPIView.as_view()),
    path("<str:snapshot_id>/custom-sections/reorder/",
         ProfileCustomSectionReorderAPIView.as_view()),

]
