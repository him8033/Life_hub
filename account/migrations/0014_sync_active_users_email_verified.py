from django.db import migrations
from django.utils import timezone


def sync_active_users_email_verified(apps, schema_editor):
    """
    Ensure all users who are currently marked as 'active' status
    have email_verified set to True and email_verified_at set.
    """
    User = apps.get_model('account', 'User')
    now = timezone.now()

    User.objects.filter(
        status__slug='active',
        email_verified=False
    ).update(
        email_verified=True,
        email_verified_at=now
    )


def reverse_sync(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0013_clean_user_role_permissions'),
    ]

    operations = [
        migrations.RunPython(sync_active_users_email_verified, reverse_sync),
    ]
