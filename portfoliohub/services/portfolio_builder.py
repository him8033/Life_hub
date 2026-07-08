from portfoliohub.services.builders.portfolio_meta_builder import (
    PortfolioMetaBuilder
)

from portfoliohub.services.builders.portfolio_theme_builder import (
    PortfolioThemeBuilder
)

from portfoliohub.services.builders.snapshot_builder import (
    SnapshotBuilder
)

from portfoliohub.services.builders.basic_info_builder import (
    BasicInfoBuilder
)

from portfoliohub.services.builders.social_link_builder import (
    SocialLinkBuilder
)

from portfoliohub.services.builders.skill_builder import (
    SkillBuilder
)

from portfoliohub.services.builders.experience_builder import (
    ExperienceBuilder
)

from portfoliohub.services.builders.education_builder import (
    EducationBuilder
)

from portfoliohub.services.builders.project_builder import (
    ProjectBuilder
)

from portfoliohub.services.builders.certificate_builder import (
    CertificateBuilder
)

from portfoliohub.services.builders.achievement_builder import (
    AchievementBuilder
)

from portfoliohub.services.builders.language_builder import (
    LanguageBuilder
)

from portfoliohub.services.builders.hobby_builder import (
    HobbyBuilder
)

from portfoliohub.services.builders.strength_builder import (
    StrengthBuilder
)

from portfoliohub.services.builders.custom_section_builder import (
    CustomSectionBuilder
)


class PortfolioBuilder:

    @staticmethod
    def build(portfolio):

        snapshot = portfolio.profile_snapshot

        return {

            # =====================================
            # CORE
            # =====================================

            "portfolio":
                PortfolioMetaBuilder.build(
                    portfolio
                ),

            "theme":
                PortfolioThemeBuilder.build(
                    portfolio.portfolio_theme
                ),

            "snapshot":
                SnapshotBuilder.build(
                    snapshot
                ),

            # =====================================
            # PROFILE
            # =====================================

            "basic_info":
                BasicInfoBuilder.build(
                    snapshot
                ),

            "social_links":
                SocialLinkBuilder.build(
                    snapshot
                ),

            "skills":
                SkillBuilder.build(
                    snapshot
                ),

            # =====================================
            # CAREER
            # =====================================

            "experiences":
                ExperienceBuilder.build(
                    snapshot
                ),

            "educations":
                EducationBuilder.build(
                    snapshot
                ),

            # =====================================
            # PROJECTS
            # =====================================

            "projects":
                ProjectBuilder.build(
                    snapshot
                ),

            # =====================================
            # CERTIFICATES
            # =====================================

            "certificates":
                CertificateBuilder.build(
                    snapshot
                ),

            # =====================================
            # ACHIEVEMENTS
            # =====================================

            "achievements":
                AchievementBuilder.build(
                    snapshot
                ),

            # =====================================
            # LANGUAGES
            # =====================================

            "languages":
                LanguageBuilder.build(
                    snapshot
                ),

            # =====================================
            # PERSONAL
            # =====================================

            "hobbies":
                HobbyBuilder.build(
                    snapshot
                ),

            "strengths":
                StrengthBuilder.build(
                    snapshot
                ),

            # =====================================
            # CUSTOM
            # =====================================

            "custom_sections":
                CustomSectionBuilder.build(
                    snapshot
                ),
        }
