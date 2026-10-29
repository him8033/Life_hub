from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers

from account.models.user import User
from account.models.otp_purpose import OTPPurpose

from account.services.auth_service import AuthService
from account.services.otp_service import OTPService
from account.services.jwt_service import JWTService

from life_hub.utils import get_client_ip


# ============================================================
# COMMON VALIDATION
# ============================================================


def validate_passwords_match(password, password2):
    if password != password2:
        raise serializers.ValidationError(
            {
                "non_field_errors": [
                    "Password and Confirm Password do not match"
                ]
            }
        )

    return password


def get_request_metadata(serializer):
    request = serializer.context.get("request")

    if not request:
        return None, None

    ip_address = get_client_ip(request)
    user_agent = request.META.get("HTTP_USER_AGENT")

    return ip_address, user_agent


# ============================================================
# REGISTER
# ============================================================


class UserRegistrationSerializer(serializers.Serializer):
    """
    Serializer for user registration with OTP verification.
    """

    email = serializers.EmailField()

    first_name = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        default="",
    )

    last_name = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        default="",
    )

    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    password2 = serializers.CharField(
        write_only=True,
    )

    tc = serializers.BooleanField(
        default=False,
    )

    def validate_tc(self, value):
        if value is False:
            raise serializers.ValidationError(
                "You must accept the Terms & Conditions."
            )

        return value

    def validate(self, attrs):
        validate_passwords_match(
            attrs.get("password"),
            attrs.get("password2"),
        )

        validate_password(
            attrs["password"]
        )

        if User.objects.filter(
            email=attrs["email"]
        ).exists():
            raise serializers.ValidationError(
                {
                    "email": [
                        "This email is already registered."
                    ]
                }
            )

        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")

        ip_address, user_agent = get_request_metadata(
            self
        )

        result = AuthService.register_user(
            email=validated_data["email"],
            first_name=validated_data.get(
                "first_name",
                "",
            ),
            last_name=validated_data.get(
                "last_name",
                "",
            ),
            password=validated_data["password"],
            tc=validated_data["tc"],
            ip_address=ip_address,
            user_agent=user_agent,
        )

        if not result["success"]:
            raise serializers.ValidationError(
                result["error"]
            )

        user = result["user"]

        return {
            "user_id": user.user_id,
            "email": user.email,
            "status": (
                user.status.slug
                if user.status
                else "pending"
            ),
            "email_verified": user.email_verified,
            "message": result["message"],
        }


# ============================================================
# LOGIN
# ============================================================


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for login validation.
    """

    email = serializers.EmailField()

    password = serializers.CharField(
        write_only=True,
    )

    def validate(self, attrs):
        ip_address, user_agent = get_request_metadata(
            self
        )

        result = AuthService.authenticate_user(
            email=attrs["email"],
            password=attrs["password"],
            ip_address=ip_address,
            user_agent=user_agent,
        )

        if not result["success"]:
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        result["error"]
                    ]
                }
            )

        self.validated_user = result["user"]

        return attrs


# ============================================================
# OTP VERIFICATION
# ============================================================


class OTPVerificationSerializer(serializers.Serializer):
    """
    Serializer for OTP verification.
    For forgot_password, accepts a reset_token and returns a confirm_token.
    """

    email = serializers.EmailField()

    otp_code = serializers.CharField(
        max_length=6,
        min_length=6,
    )

    purpose = serializers.ChoiceField(
        choices=[
            "email_verification",
            "forgot_password",
            "login",
        ]
    )

    reset_token = serializers.CharField(required=False)  # JWT token from forgot password

    def validate(self, attrs):
        try:
            user = User.objects.get(
                email=attrs["email"]
            )
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {
                    "email": [
                        "No user found with this email address"
                    ]
                }
            )

        # For forgot_password, validate the reset_token
        if attrs["purpose"] == "forgot_password":
            reset_token = attrs.get("reset_token")
            if not reset_token:
                raise serializers.ValidationError(
                    {
                        "non_field_errors": [
                            "Reset token is required for password reset"
                        ]
                    }
                )

            from account.services.jwt_service import JWTService
            token_validation = JWTService.validate_password_reset_token(
                reset_token,
                "request"
            )

            if not token_validation["valid"]:
                raise serializers.ValidationError(
                    {
                        "non_field_errors": [
                            token_validation.get("error", "Invalid reset token")
                        ]
                    }
                )

            # Verify the token matches the email
            if token_validation["email"] != attrs["email"]:
                raise serializers.ValidationError(
                    {
                        "non_field_errors": [
                            "Reset token does not match the provided email"
                        ]
                    }
                )

        result = OTPService.verify_otp(
            user=user,
            purpose_slug=attrs["purpose"],
            code=attrs["otp_code"],
        )

        if not result["success"]:
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        result["error"]
                    ]
                }
            )

        self.validated_user = user
        self.validated_purpose = attrs["purpose"]

        # For forgot_password, mark the request token as used and generate a confirm token
        if attrs["purpose"] == "forgot_password":
            from account.services.jwt_service import JWTService
            JWTService.validate_password_reset_token(
                reset_token,
                "request",
                mark_as_used=True
            )
            confirm_token = JWTService.generate_password_reset_confirm_token(user, attrs["email"])
            attrs["confirm_token"] = confirm_token

        return attrs


# ============================================================
# OTP RESEND
# ============================================================


class OTPResendSerializer(serializers.Serializer):
    """
    Serializer for resending OTP.
    """

    email = serializers.EmailField()

    purpose = serializers.ChoiceField(
        choices=[
            "email_verification",
            "forgot_password",
            "login",
        ]
    )

    def validate(self, attrs):
        try:
            user = User.objects.get(
                email=attrs["email"]
            )
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {
                    "email": [
                        "No user found with this email address"
                    ]
                }
            )

        ip_address, user_agent = get_request_metadata(
            self
        )

        result = OTPService.generate_otp(
            user=user,
            purpose_slug=attrs["purpose"],
            ip_address=ip_address,
            user_agent=user_agent,
        )

        if not result["success"]:
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        result["error"]
                    ]
                }
            )

        purpose_obj = OTPPurpose.objects.filter(
            slug=attrs["purpose"],
            is_active=True
        ).first()
        if purpose_obj:
            attrs["cooldown_seconds"] = purpose_obj.resend_cooldown_seconds

        if attrs["purpose"] == "forgot_password":
            from account.services.jwt_service import JWTService
            reset_token = JWTService.generate_password_reset_token(user, attrs["email"])
            attrs["reset_token"] = reset_token

        return attrs


# ============================================================
# FORGOT PASSWORD
# ============================================================


class PasswordForgotSerializer(serializers.Serializer):
    """
    Serializer for requesting password reset OTP.
    Returns a JWT token for the next step.
    """

    email = serializers.EmailField()

    def validate(self, attrs):
        try:
            user = User.objects.get(
                email=attrs["email"]
            )
        except User.DoesNotExist:
            # Do not reveal whether the email exists.
            return attrs

        ip_address, user_agent = get_request_metadata(
            self
        )

        result = OTPService.generate_otp(
            user=user,
            purpose_slug="forgot_password",
            ip_address=ip_address,
            user_agent=user_agent,
        )

        if not result["success"]:
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        result["error"]
                    ]
                }
            )

        # Generate secure random token for password reset flow
        from account.services.jwt_service import JWTService
        reset_token = JWTService.generate_password_reset_token(user, attrs["email"])

        # Store token in attrs to return in response
        attrs["reset_token"] = reset_token

        return attrs


# ============================================================
# RESET PASSWORD
# ============================================================


class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for resetting password with confirm_token.
    Uses JWT token instead of requiring OTP again.
    """

    email = serializers.EmailField()

    confirm_token = serializers.CharField(required=True)  # JWT token from OTP verification

    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    password2 = serializers.CharField(
        write_only=True,
    )

    def validate(self, attrs):
        validate_passwords_match(
            attrs.get("password"),
            attrs.get("password2"),
        )

        validate_password(
            attrs["password"]
        )

        # Validate the confirm_token
        confirm_token = attrs.get("confirm_token")
        if not confirm_token:
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        "Confirm token is required"
                    ]
                }
            )

        from account.services.jwt_service import JWTService
        token_validation = JWTService.validate_password_reset_token(
            confirm_token,
            "confirm"
        )

        if not token_validation["valid"]:
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        token_validation.get("error", "Invalid confirm token")
                    ]
                }
            )

        # Verify the token matches the email
        if token_validation["email"] != attrs["email"]:
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        "Confirm token does not match the provided email"
                    ]
                }
            )

        try:
            user = User.objects.get(
                email=attrs["email"]
            )
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {
                    "email": [
                        "No user found with this email address"
                    ]
                }
            )

        self.validated_user = user

        return attrs

    def save(self, **kwargs):
        from account.services.session_service import (
            SessionService
        )
        from account.services.status_service import (
            StatusService
        )
        from django.utils import timezone

        user = self.validated_user

        user.set_password(
            self.validated_data["password"]
        )

        update_fields = ["password"]

        if not user.email_verified:
            user.email_verified = True
            user.email_verified_at = timezone.now()
            update_fields.extend(["email_verified", "email_verified_at"])

        if user.status and user.status.slug == "pending":
            StatusService.update_user_status(
                user,
                "active"
            )

        user.save(
            update_fields=update_fields
        )

        SessionService.revoke_all_sessions(
            user
        )

        # Mark confirm_token as used to prevent replay attacks
        from account.services.jwt_service import JWTService
        confirm_token = self.validated_data.get("confirm_token")
        if confirm_token:
            JWTService.validate_password_reset_token(
                confirm_token,
                "confirm",
                mark_as_used=True
            )

        return {
            "message": "Password reset successfully"
        }


# ============================================================
# CHANGE PASSWORD
# ============================================================


class UserChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing the current user's password.
    """

    old_password = serializers.CharField(
        write_only=True,
    )

    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    password2 = serializers.CharField(
        write_only=True,
    )

    def validate(self, attrs):
        validate_passwords_match(
            attrs.get("password"),
            attrs.get("password2"),
        )

        validate_password(
            attrs["password"]
        )

        user = self.context.get("user")

        if not user:
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        "Authenticated user is required."
                    ]
                }
            )

        if not user.check_password(attrs["old_password"]):
            raise serializers.ValidationError(
                {
                    "old_password": [
                        "Current password is incorrect."
                    ]
                }
            )

        return attrs

    def save(self, **kwargs):
        user = self.context.get("user")
        return AuthService.change_password(
            user=user,
            old_password=self.validated_data["old_password"],
            new_password=self.validated_data["password"],
        )


# ============================================================
# TOKEN REFRESH
# ============================================================


class TokenRefreshSerializer(serializers.Serializer):
    """
    Serializer for refreshing JWT tokens.
    """

    refresh = serializers.CharField(
        write_only=True,
    )

    def validate(self, attrs):
        result = JWTService.refresh_tokens(
            attrs["refresh"]
        )

        if not result["success"]:
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        result["error"]
                    ]
                }
            )

        return result


# ============================================================
# CURRENT USER PROFILE
# ============================================================


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for returning user profile information.
    """

    roles = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()

    created_at = serializers.DateTimeField(
        format="%Y-%m-%dT%H:%M:%S.%fZ"
    )

    class Meta:
        model = User

        fields = [
            "user_id",
            "email",
            "first_name",
            "last_name",
            "roles",
            "status",
            "email_verified",
            "is_active",
            "profile_image",
            "created_at",
        ]

    def get_roles(self, obj):
        return list(
            obj.roles.values_list(
                "slug",
                flat=True,
            )
        )

    def get_status(self, obj):
        return (
            obj.status.slug
            if obj.status
            else None
        )

    def get_profile_image(self, obj):
        try:
            if hasattr(obj, 'profile') and obj.profile and obj.profile.profile_image:
                return obj.profile.profile_image.url
        except Exception:
            pass
        return None


# ============================================================
# SOCIAL LOGIN
# ============================================================


class SocialLoginSerializer(serializers.Serializer):
    """
    Serializer for Google/GitHub social login.
    """

    provider = serializers.ChoiceField(choices=["google", "github"])
    token = serializers.CharField(
        help_text="Google ID token or GitHub authorization code"
    )

    def validate(self, attrs):
        from account.services.social_auth_service import SocialAuthService

        provider = attrs["provider"]
        token = attrs["token"]
        request = self.context.get("request")

        if provider == "google":
            result = SocialAuthService.authenticate_google(token, request=request)
        elif provider == "github":
            result = SocialAuthService.authenticate_github(token, request=request)
        else:
            raise serializers.ValidationError({"provider": ["Unsupported provider"]})

        if not result["success"]:
            raise serializers.ValidationError(
                {"non_field_errors": [result["error"]]}
            )

        attrs["auth_result"] = result
        return attrs
