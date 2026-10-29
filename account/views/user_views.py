from django.utils import timezone

from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView

from account.serializers.user import (
    PasswordForgotSerializer,
    UserChangePasswordSerializer,
    PasswordResetSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    TokenRefreshSerializer,
    OTPVerificationSerializer,
    OTPResendSerializer,
)

from account.renderers import UserRenderer

from account.services.auth_service import AuthService
from account.services.session_service import SessionService
from account.services.status_service import StatusService


# ============================================================
# REGISTER
# ============================================================


class UserRegistrationView(APIView):
    """
    Register a new user.

    Flow:
        Register
            ↓
        OTP sent
            ↓
        Verify OTP
            ↓
        Account activated
    """

    renderer_classes = [UserRenderer]
    permission_classes = [AllowAny]

    def post(self, request):

        serializer = UserRegistrationSerializer(
            data=request.data,
            context={
                "request": request
            }
        )

        serializer.is_valid(
            raise_exception=True
        )

        user_data = serializer.save()

        return Response(
            {
                "message": (
                    "Registration successful. "
                    "Please verify your email."
                ),
                "data": user_data,
            },
            status=status.HTTP_201_CREATED,
        )


# ============================================================
# LOGIN
# ============================================================


class UserLoginView(APIView):
    """
    Login user and generate JWT tokens.
    """

    renderer_classes = [UserRenderer]
    permission_classes = [AllowAny]

    def post(self, request):

        serializer = UserLoginSerializer(
            data=request.data,
            context={
                "request": request
            }
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = serializer.validated_user

        result = AuthService.login_user(
            user,
            request
        )

        if not result["success"]:

            return Response(
                {
                    "message": result["error"],
                    "data": None,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Add user profile information to response
        roles_list = list(user.roles.values_list("slug", flat=True))
        primary_role = "admin" if "admin" in roles_list or user.is_superuser else (roles_list[0] if roles_list else "user")
        user_profile = {
            "user_id": user.user_id,
            "email": user.email,
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "full_name": user.full_name,
            "role": primary_role,
            "roles": roles_list,
            "is_superuser": user.is_superuser,
            "status": user.status.slug if user.status else "pending",
            "email_verified": user.email_verified,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }

        # Add profile image if available
        profile_image = None
        try:
            if hasattr(user, 'profile') and user.profile and user.profile.profile_image:
                profile_image = user.profile.profile_image.url
        except Exception:
            pass

        user_profile["profile_image"] = profile_image

        # Combine login result with user profile
        result["user"] = user_profile

        return Response(
            {
                "message": "Login successful",
                "data": result,
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# OTP VERIFY
# ============================================================


class OTPVerificationView(APIView):
    """
    Verify OTP.

    Supported purposes:
        - email_verification
        - forgot_password
    """

    renderer_classes = [UserRenderer]
    permission_classes = [AllowAny]

    def post(self, request):

        serializer = OTPVerificationSerializer(
            data=request.data,
            context={
                "request": request
            }
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = serializer.validated_user
        purpose = serializer.validated_purpose

        # ----------------------------------------------------
        # EMAIL VERIFICATION
        # ----------------------------------------------------

        if purpose == "email_verification":

            user.email_verified = True
            user.email_verified_at = timezone.now()

            StatusService.update_user_status(
                user,
                "active"
            )

            user.save(
                update_fields=[
                    "email_verified",
                    "email_verified_at",
                ]
            )

            login_result = AuthService.login_user(
                user,
                request,
                login_method="email_verification"
            )

            return Response(
                {
                    "message": "Email verified successfully",
                    "data": login_result if login_result.get("success") else None,
                },
                status=status.HTTP_200_OK,
            )

        # ----------------------------------------------------
        # FORGOT PASSWORD
        # ----------------------------------------------------

        if purpose == "forgot_password":

            # Mark email as verified since OTP was delivered to and verified from this email
            if not user.email_verified:
                user.email_verified = True
                user.email_verified_at = timezone.now()
                user.save(
                    update_fields=[
                        "email_verified",
                        "email_verified_at",
                    ]
                )

            if user.status and user.status.slug == "pending":
                StatusService.update_user_status(
                    user,
                    "active"
                )

            # Get the confirm_token from serializer
            confirm_token = serializer.validated_data.get("confirm_token")

            return Response(
                {
                    "message": (
                        "OTP verified. "
                        "Proceed to reset password."
                    ),
                    "data": {
                        "confirm_token": confirm_token,
                    },
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "message": "OTP verified successfully",
                "data": None,
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# OTP RESEND
# ============================================================


class OTPResendView(APIView):
    """
    Resend OTP.
    """

    renderer_classes = [UserRenderer]
    permission_classes = [AllowAny]

    def post(self, request):

        serializer = OTPResendSerializer(
            data=request.data,
            context={
                "request": request
            }
        )

        serializer.is_valid(
            raise_exception=True
        )

        data = {}
        if "reset_token" in serializer.validated_data:
            data["reset_token"] = serializer.validated_data["reset_token"]
        if "cooldown_seconds" in serializer.validated_data:
            data["cooldown_seconds"] = serializer.validated_data["cooldown_seconds"]

        return Response(
            {
                "message": "OTP sent successfully",
                "data": data if data else None,
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# FORGOT PASSWORD
# ============================================================


class PasswordForgotView(APIView):
    """
    Request password reset OTP.
    Returns a JWT token for the next step.
    """

    renderer_classes = [UserRenderer]
    permission_classes = [AllowAny]

    def post(self, request):

        serializer = PasswordForgotSerializer(
            data=request.data,
            context={
                "request": request
            }
        )

        serializer.is_valid(
            raise_exception=True
        )

        # Get the reset token from serializer
        reset_token = serializer.validated_data.get("reset_token")

        return Response(
            {
                "message": (
                    "Password reset OTP sent "
                    "to your email"
                ),
                "data": {
                    "reset_token": reset_token
                },
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# RESET PASSWORD
# ============================================================


class PasswordResetView(APIView):
    """
    Reset password after OTP verification.
    """

    renderer_classes = [UserRenderer]
    permission_classes = [AllowAny]

    def post(self, request):

        serializer = PasswordResetSerializer(
            data=request.data,
            context={
                "request": request
            }
        )

        serializer.is_valid(
            raise_exception=True
        )

        result = serializer.save()

        return Response(
            {
                "message": "Password reset successfully",
                "data": result,
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# CHANGE PASSWORD
# ============================================================


class UserChangePasswordView(APIView):
    """
    Change password for currently authenticated user.
    """

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = UserChangePasswordSerializer(
            data=request.data,
            context={
                "user": request.user
            }
        )

        serializer.is_valid(
            raise_exception=True
        )

        result = serializer.save()

        return Response(
            {
                "message": (
                    result.get("message")
                    if isinstance(result, dict) and result.get("message")
                    else "Password changed successfully. All sessions have been revoked."
                ),
                "data": None,
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# PROFILE
# ============================================================


class UserProfileView(APIView):
    """
    Get currently authenticated user's profile.
    """

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request):

        serializer = UserProfileSerializer(
            request.user
        )

        return Response(
            {
                "message": "Profile fetched successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# TOKEN REFRESH
# ============================================================


class UserTokenRefreshView(TokenRefreshView):
    """
    Refresh JWT access token.
    """

    serializer_class = TokenRefreshSerializer
    renderer_classes = [UserRenderer]


# ============================================================
# LOGOUT CURRENT DEVICE
# ============================================================


class LogoutView(APIView):
    """
    Logout current device.
    """

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from account.services.session_service import SessionService

        session_id = request.data.get('session_id')

        # Revoke the current session if session_id is provided
        if session_id:
            SessionService.revoke_session(session_id, reason='logout')

        return Response(
            {
                "message": "Logged out successfully",
                "data": None,
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# LOGOUT ALL DEVICES
# ============================================================


class LogoutAllView(APIView):
    """
    Logout from all devices.
    """

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request):

        revoked_count = (
            SessionService.revoke_all_sessions(
                request.user
            )
        )

        return Response(
            {
                "message": (
                    "Logged out from all devices successfully"
                ),
                "data": {
                    "revoked_sessions": revoked_count
                },
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# SOCIAL LOGIN
# ============================================================


class SocialLoginView(APIView):
    """
    Social login endpoint (Google / GitHub).
    """

    permission_classes = [AllowAny]
    renderer_classes = [UserRenderer]

    def post(self, request):
        from account.serializers.user import SocialLoginSerializer

        serializer = SocialLoginSerializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        auth_result = serializer.validated_data["auth_result"]

        return Response(
            {
                "message": "Social login successful",
                "data": auth_result,
            },
            status=status.HTTP_200_OK,
        )
