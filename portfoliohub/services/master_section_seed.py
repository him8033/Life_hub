# portfoliohub/services/master_section_seed.py

from portfoliohub.models.master_section import (
    MasterSection
)


class MasterSectionSeedService:

    SECTIONS = [
        ("basic_info", "Basic Information"),
        ("experience", "Experience"),
        ("education", "Education"),
        ("skill", "Skills"),
        ("project", "Projects"),
        ("certificate", "Certificates"),
        ("achievement", "Achievements"),
        ("language", "Languages"),
        ("hobby", "Hobbies"),
        ("strength", "Strengths"),
        ("social_link", "Social Links"),
        ("custom_section", "Custom Sections"),
    ]

    @classmethod
    def seed(cls):

        for key, name in cls.SECTIONS:

            MasterSection.objects.get_or_create(
                key=key,
                defaults={
                    "name": name,
                    "is_active": True,
                }
            )