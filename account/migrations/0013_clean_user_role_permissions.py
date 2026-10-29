from django.db import migrations


def clean_user_role_permissions(apps, schema_editor):
    """
    Remove administrative permissions from the standard 'user' role.
    Standard users should only have user-level permissions (e.g., portfolio.manage, resume.manage),
    never administrative user management or role management permissions.
    """
    Role = apps.get_model('account', 'Role')
    RolePermission = apps.get_model('account', 'RolePermission')

    user_role = Role.objects.filter(slug='user').first()
    if not user_role:
        return

    # Permissions that must NOT be granted to the standard user role
    disallowed_prefixes = (
        'user.',
        'role.',
        'rolepermission.',
        'permission.',
        'status.',
        'otppurpose.',
        'otp.',
        'socialprovider.',
        'socialaccount.',
        'usersession.',
        'loginhistory.',
    )

    # Delete any RolePermission records for 'user' role that match administrative prefixes
    for rp in RolePermission.objects.filter(role=user_role):
        perm_slug = rp.permission.slug
        if any(perm_slug.startswith(prefix) for prefix in disallowed_prefixes):
            rp.delete()


def rollback_user_role_permissions(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0012_seed_rbac_permissions'),
    ]

    operations = [
        migrations.RunPython(clean_user_role_permissions, rollback_user_role_permissions),
    ]
