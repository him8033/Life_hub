from django.contrib.auth.password_validation import (
    validate_password
)

from rest_framework import serializers

from account.models.user import User
from account.models import Role, UserRole


# ============================================================
# USER EDIT
# ============================================================


class UserEditSerializer(serializers.ModelSerializer):
    """
    Admin serializer for updating a user.

    Supports:
    - Basic profile fields
    - Roles
    - Password
    """

    roles = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=False,
        help_text="List of role slugs to assign to the user",
    )

    new_password = serializers.CharField(
        write_only=True,
        required=False,
        min_length=8,
    )

    confirm_password = serializers.CharField(
        write_only=True,
        required=False,
    )

    send_email = serializers.BooleanField(
        default=False,
        help_text=(
            "Send email notification for role "
            "or password changes"
        ),
    )

    class Meta:
        model = User

        fields = [
            "first_name",
            "last_name",
            "phone_number",
            "roles",
            "new_password",
            "confirm_password",
            "send_email",
        ]

    def validate(self, attrs):
        new_password = attrs.get("new_password")
        confirm_password = attrs.get("confirm_password")

        # Password fields must be supplied together
        if new_password or confirm_password:

            if not new_password or not confirm_password:
                raise serializers.ValidationError(
                    {
                        "non_field_errors": [
                            (
                                "Both new_password and "
                                "confirm_password are required."
                            )
                        ]
                    }
                )

            if new_password != confirm_password:
                raise serializers.ValidationError(
                    {
                        "non_field_errors": [
                            (
                                "New password and confirm "
                                "password do not match."
                            )
                        ]
                    }
                )

            validate_password(new_password)

        # Remove confirm_password before model handling
        attrs.pop("confirm_password", None)

        return attrs


# ============================================================
# USER STATUS / BLOCK / UNBLOCK
# ============================================================


class UserStatusUpdateSerializer(serializers.Serializer):
    """
    Admin serializer for updating user status
    or blocking/unblocking a user.

    Supported actions:

    1. status
       {
           "status_slug": "active"
       }

    2. block
       {
           "action": "block",
           "reason": "Policy violation"
       }

    3. unblock
       {
           "action": "unblock",
           "reason": "Issue resolved"
       }
    """

    status_slug = serializers.CharField(
        required=False,
        help_text="Status slug to assign to the user",
    )

    action = serializers.ChoiceField(
        choices=[
            "block",
            "unblock",
        ],
        required=False,
        help_text="Action to perform: block or unblock",
    )

    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        help_text="Reason for status/block action",
    )

    send_email = serializers.BooleanField(
        default=False,
        help_text=(
            "Send email notification to user "
            "about status change"
        ),
    )

    def validate(self, attrs):
        status_slug = attrs.get("status_slug")
        action = attrs.get("action")

        if not status_slug and not action:
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        (
                            "Either status_slug or action "
                            "is required."
                        )
                    ]
                }
            )

        if status_slug and action:
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        (
                            "Provide either status_slug "
                            "or action, not both."
                        )
                    ]
                }
            )

        return attrs


# ============================================================
# USER DELETE
# ============================================================


class UserDeleteSerializer(serializers.Serializer):
    """
    Admin serializer for soft deleting or permanently
    deleting a user.
    """

    permanent = serializers.BooleanField(
        default=False,
        help_text=(
            "Permanently delete user. "
            "Soft delete if False."
        ),
    )

    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        help_text="Reason for deletion",
    )

    send_email = serializers.BooleanField(
        default=False,
        help_text=(
            "Send email notification to user "
            "about deletion"
        ),
    )


# ============================================================
# ADMIN USER CREATE
# ============================================================


class AdminUserCreateSerializer(serializers.Serializer):
    """
    Admin serializer for creating a new user without OTP verification.
    User will be created with pending status by default.
    """

    email = serializers.EmailField(
        help_text="User email address"
    )

    first_name = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        default="",
        help_text="User first name"
    )

    last_name = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        default="",
        help_text="User last name"
    )

    phone_number = serializers.CharField(
        max_length=15,
        required=False,
        allow_blank=True,
        default="",
        help_text="User phone number"
    )

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        help_text="User password (min 8 characters)"
    )

    confirm_password = serializers.CharField(
        write_only=True,
        help_text="Confirm password"
    )

    roles = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=False,
        help_text="List of role slugs to assign to the user (default: ['user'])"
    )

    send_email = serializers.BooleanField(
        default=False,
        help_text="Send welcome email to the user"
    )

    def validate(self, attrs):
        # Validate password match
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")

        if password != confirm_password:
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        "Password and confirm password do not match"
                    ]
                }
            )

        # Validate password strength
        validate_password(password)

        # Check if email already exists
        if User.objects.filter(email=attrs["email"]).exists():
            raise serializers.ValidationError(
                {
                    "email": [
                        "This email is already registered"
                    ]
                }
            )

        # Validate roles if provided
        roles = attrs.get("roles")
        if roles:
            for role_slug in roles:
                if not Role.objects.filter(slug=role_slug).exists():
                    raise serializers.ValidationError(
                        {
                            "roles": [
                                f"Role '{role_slug}' does not exist"
                            ]
                        }
                    )

        return attrs

    def create(self, validated_data):
        from account.services.auth_service import AuthService

        # Remove confirm_password and send_email, but keep password
        validated_data.pop("confirm_password")
        send_email = validated_data.pop("send_email", False)
        password = validated_data.get("password")

        # Get admin user from context
        admin_user = self.context.get("admin_user")

        # Create user via AuthService
        result = AuthService.admin_create_user(
            email=validated_data["email"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            phone_number=validated_data.get("phone_number", ""),
            password=password,
            roles=validated_data.get("roles", ["user"]),
            created_by=admin_user
        )

        if not result["success"]:
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        result["error"]
                    ]
                }
            )

        # Send welcome email if requested
        if send_email:
            from account.services.email_service import EmailService
            user = result["user"]
            EmailService.send_admin_welcome_email(
                to_email=user.email,
                user_name=user.full_name or user.email,
                password=password
            )

        return {
            "user_id": result["user"].user_id,
            "email": result["user"].email,
            "status": result["user"].status.slug if result["user"].status else "pending",
            "roles": list(result["user"].roles.values_list("slug", flat=True)),
            "message": "User created successfully with pending status"
        }
