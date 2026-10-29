from django.db import migrations
from life_hub.utils import generate_ulid_with_prefix


def seed_rbac_permissions(apps, schema_editor):
    Permission = apps.get_model('account', 'Permission')
    Role = apps.get_model('account', 'Role')
    RolePermission = apps.get_model('account', 'RolePermission')

    permissions_data = [
        # User management
        ("user.list", "List Users", "user", "List all users"),
        ("user.view", "View User", "user", "View detailed user information"),
        ("user.edit", "Edit User", "user", "Edit user profile and account details"),
        ("user.role.update", "Update User Role", "user", "Update user assigned roles"),
        ("user.status.update", "Update User Status", "user", "Update user account status"),

        # Role management
        ("role.create", "Create Role", "role", "Create new system roles"),
        ("role.list", "List Roles", "role", "List all system roles"),
        ("role.view", "View Role", "role", "View detailed role information"),
        ("role.edit", "Edit Role", "role", "Edit role name and properties"),
        ("role.delete", "Delete Role", "role", "Delete system roles"),

        # Permission management
        ("permission.create", "Create Permission", "permission", "Create new system permissions"),
        ("permission.list", "List Permissions", "permission", "List all system permissions"),
        ("permission.view", "View Permission", "permission", "View detailed permission information"),
        ("permission.edit", "Edit Permission", "permission", "Edit permission properties"),
        ("permission.delete", "Delete Permission", "permission", "Delete system permissions"),

        # Role Permission management
        ("rolepermission.create", "Assign Role Permission", "rolepermission", "Assign permission to a role"),
        ("rolepermission.list", "List Role Permissions", "rolepermission", "List role permissions"),
        ("rolepermission.view", "View Role Permission", "rolepermission", "View role permission details"),
        ("rolepermission.delete", "Remove Role Permission", "rolepermission", "Revoke permission from a role"),

        # Status management
        ("status.create", "Create Status", "status", "Create new user statuses"),
        ("status.list", "List Statuses", "status", "List all user statuses"),
        ("status.view", "View Status", "status", "View detailed status information"),
        ("status.edit", "Edit Status", "status", "Edit user status properties"),
        ("status.delete", "Delete Status", "status", "Delete user statuses"),

        # OTP Purpose management
        ("otppurpose.create", "Create OTP Purpose", "otppurpose", "Create new OTP purpose types"),
        ("otppurpose.list", "List OTP Purposes", "otppurpose", "List all OTP purposes"),
        ("otppurpose.view", "View OTP Purpose", "otppurpose", "View detailed OTP purpose information"),
        ("otppurpose.edit", "Edit OTP Purpose", "otppurpose", "Edit OTP purpose configuration"),
        ("otppurpose.delete", "Delete OTP Purpose", "otppurpose", "Delete OTP purposes"),

        # OTP Records
        ("otp.list", "List OTPs", "otp", "List OTP audit logs"),
        ("otp.view", "View OTP", "otp", "View detailed OTP audit information"),

        # Login History
        ("loginhistory.list", "List Login History", "loginhistory", "List login audit records"),
        ("loginhistory.view", "View Login History", "loginhistory", "View detailed login record"),

        # User Sessions
        ("usersession.list", "List User Sessions", "usersession", "List active user sessions"),
        ("usersession.view", "View User Session", "usersession", "View user session details"),
        ("usersession.delete", "Revoke User Session", "usersession", "Revoke active user sessions"),

        # Social Providers
        ("socialprovider.create", "Create Social Provider", "socialprovider", "Create OAuth provider configuration"),
        ("socialprovider.list", "List Social Providers", "socialprovider", "List OAuth providers"),
        ("socialprovider.view", "View Social Provider", "socialprovider", "View OAuth provider details"),
        ("socialprovider.edit", "Edit Social Provider", "socialprovider", "Edit OAuth provider settings"),
        ("socialprovider.delete", "Delete Social Provider", "socialprovider", "Delete OAuth provider configuration"),

        # Social Accounts
        ("socialaccount.create", "Create Social Account Link", "socialaccount", "Link social account"),
        ("socialaccount.list", "List Social Accounts", "socialaccount", "List linked social accounts"),
        ("socialaccount.view", "View Social Account", "socialaccount", "View linked social account details"),
        ("socialaccount.edit", "Edit Social Account", "socialaccount", "Edit linked social account"),
        ("socialaccount.delete", "Delete Social Account Link", "socialaccount", "Unlink social account"),
    ]

    # Find admin role
    admin_role = Role.objects.filter(slug='admin').first()

    for slug, name, module, description in permissions_data:
        perm, created = Permission.objects.get_or_create(
            slug=slug,
            defaults={
                'permission_id': generate_ulid_with_prefix('perm'),
                'name': name,
                'module': module,
                'description': description,
                'is_active': True,
            }
        )

        if admin_role:
            RolePermission.objects.get_or_create(
                role=admin_role,
                permission=perm,
                defaults={
                    'rolepermission_id': generate_ulid_with_prefix('rp')
                }
            )


def rollback_rbac_permissions(apps, schema_editor):
    Permission = apps.get_model('account', 'Permission')
    # Can delete newly added slugs if needed
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0011_passwordresettoken'),
    ]

    operations = [
        migrations.RunPython(seed_rbac_permissions, rollback_rbac_permissions),
    ]
