# portfoliohub/signals.py

from django.db.models.signals import post_migrate
from django.dispatch import receiver

from portfoliohub.services.master_section_seed import (
    MasterSectionSeedService
)


@receiver(post_migrate)
def seed_master_sections(sender, **kwargs):

    if sender.name != "portfoliohub":
        return

    MasterSectionSeedService.seed()
