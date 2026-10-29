from django.contrib import admin
from account.models.user import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from account.models import Role, Permission, UserRole, RolePermission, UserStatus, OTPPurpose, OTP, SocialProvider, SocialAccount, UserSession, LoginHistory


class UserModelAdmin(BaseUserAdmin):
    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserModelAdmin
    # that reference specific fields on auth.User.
    list_display = ["id", "user_id", "email", "first_name", "last_name", "status", "email_verified", "is_staff", "tc"]
    list_filter = ["status", "email_verified", "is_staff", "is_superuser", "created_at"]
    fieldsets = [
        ('User Credentials', {"fields": ["email", "password"]}),
        ("Personal info", {"fields": ["first_name", "last_name", "phone_number", "tc"]}),
        ("Verification", {"fields": ["email_verified", "email_verified_at", "phone_verified", "phone_verified_at"]}),
        ("Status", {"fields": ["status"]}),
        ("Permissions", {"fields": ["is_active", "is_staff", "is_superuser"]}),
        ("Security", {"fields": ["last_login_ip", "last_seen", "deleted_at"]}),
    ]
    # add_fieldsets is not a standard ModelAdmin attribute. UserModelAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email", "first_name", "last_name", "tc", "password1", "password2"],
            },
        ),
    ]
    search_fields = ["email", "first_name", "last_name", "user_id"]
    ordering = ["-created_at"]
    filter_horizontal = []
    readonly_fields = ["user_id", "email_verified_at", "phone_verified_at", "last_login_ip", "last_seen", "created_at", "updated_at"]


# Now register the new UserModelAdmin...
admin.site.register(User, UserModelAdmin)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ["id", "role_id", "name", "slug", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "slug", "role_id"]
    readonly_fields = ["role_id", "created_at", "updated_at"]


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ["id", "permission_id", "name", "slug", "module", "is_active", "created_at"]
    list_filter = ["module", "is_active", "created_at"]
    search_fields = ["name", "slug", "permission_id", "module"]
    readonly_fields = ["permission_id", "created_at", "updated_at"]


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ["id", "userrole_id", "user", "role", "assigned_by", "assigned_at"]
    list_filter = ["role", "assigned_at"]
    search_fields = ["user__email", "role__name", "userrole_id"]
    readonly_fields = ["userrole_id", "assigned_at", "created_at", "updated_at"]


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ["id", "rolepermission_id", "role", "permission", "created_at"]
    list_filter = ["role", "permission__module"]
    search_fields = ["role__name", "permission__slug", "rolepermission_id"]
    readonly_fields = ["rolepermission_id", "created_at", "updated_at"]


@admin.register(UserStatus)
class UserStatusAdmin(admin.ModelAdmin):
    list_display = ["id", "userstatus_id", "name", "slug", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "slug", "userstatus_id"]
    readonly_fields = ["userstatus_id", "created_at", "updated_at"]


@admin.register(OTPPurpose)
class OTPPurposeAdmin(admin.ModelAdmin):
    list_display = ["id", "otppurpose_id", "name", "slug", "expiry_seconds", "max_attempts", "resend_cooldown_seconds", "is_active"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "slug", "otppurpose_id"]
    readonly_fields = ["otppurpose_id", "created_at", "updated_at"]


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ["id", "otp_id", "user", "purpose", "attempts", "is_used", "expires_at", "created_at"]
    list_filter = ["purpose", "is_used", "created_at"]
    search_fields = ["user__email", "otp_id"]
    readonly_fields = ["otp_id", "created_at", "updated_at"]
    exclude = ["code_hash"]  # Hide sensitive code_hash


@admin.register(SocialProvider)
class SocialProviderAdmin(admin.ModelAdmin):
    list_display = ["id", "socialprovider_id", "name", "slug", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "slug", "socialprovider_id"]
    readonly_fields = ["socialprovider_id", "created_at", "updated_at"]


@admin.register(SocialAccount)
class SocialAccountAdmin(admin.ModelAdmin):
    list_display = ["id", "socialaccount_id", "user", "provider", "provider_user_id", "linked_at"]
    list_filter = ["provider", "linked_at"]
    search_fields = ["user__email", "provider_user_id", "socialaccount_id"]
    readonly_fields = ["socialaccount_id", "linked_at", "updated_at"]


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ["id", "usersession_id", "user", "device", "browser", "ip_address", "is_active", "last_activity_at", "expires_at"]
    list_filter = ["is_active", "device", "created_at"]
    search_fields = ["user__email", "ip_address", "usersession_id"]
    readonly_fields = ["usersession_id", "created_at", "updated_at"]
    exclude = ["refresh_token_hash"]  # Hide sensitive refresh_token_hash


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ["id", "loginhistory_id", "user", "login_method", "success", "ip_address", "created_at"]
    list_filter = ["login_method", "success", "created_at"]
    search_fields = ["user__email", "ip_address", "loginhistory_id"]
    readonly_fields = ["loginhistory_id", "created_at"]