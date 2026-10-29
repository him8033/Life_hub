# account/urls.py

from django.urls import path

# =========================
# AUTH VIEWS
# =========================
from account.views.user_views import (
    PasswordForgotView,
    UserChangePasswordView,
    PasswordResetView,
    UserRegistrationView,
    UserLoginView,
    UserTokenRefreshView,
    OTPVerificationView,
    OTPResendView,
    LogoutView,
    LogoutAllView,
    UserProfileView,
    SocialLoginView,
)


# ============================================================
# USER MANAGEMENT VIEWS
# ============================================================

from account.views.user_crud import (
    UserCreateView,
    UserListView,
    UserDetailView,
    UserEditView,
    UserStatusUpdateView,
    UserDeleteView,
)


# ============================================================
# ROLE MANAGEMENT VIEWS
# ============================================================

from account.views.role_crud import (
    RoleCreateView,
    RoleListView,
    RoleDetailView,
    RoleEditView,
    RoleDeleteView,
)


# ============================================================
# ROLE PERMISSION MANAGEMENT VIEWS
# ============================================================

from account.views.rolepermission_crud import (
    RolePermissionCreateView,
    RolePermissionListView,
    RolePermissionDetailView,
    RolePermissionDeleteView,
)


# ============================================================
# STATUS MANAGEMENT VIEWS
# ============================================================

from account.views.status_crud import (
    StatusCreateView,
    StatusListView,
    StatusDetailView,
    StatusEditView,
    StatusDeleteView,
)


# ============================================================
# OTP PURPOSE MANAGEMENT VIEWS
# ============================================================

from account.views.otppurpose_crud import (
    OTPPurposeCreateView,
    OTPPurposeListView,
    OTPPurposeDetailView,
    OTPPurposeEditView,
    OTPPurposeDeleteView,
)


# ============================================================
# PERMISSION MANAGEMENT VIEWS
# ============================================================

from account.views.permission_crud import (
    PermissionCreateView,
    PermissionListView,
    PermissionDetailView,
    PermissionEditView,
    PermissionDeleteView,
)


# ============================================================
# SOCIAL PROVIDER MANAGEMENT VIEWS
# ============================================================

from account.views.socialprovider_crud import (
    SocialProviderCreateView,
    SocialProviderListView,
    SocialProviderDetailView,
    SocialProviderEditView,
    SocialProviderDeleteView,
)


# ============================================================
# SOCIAL ACCOUNT MANAGEMENT VIEWS
# ============================================================

from account.views.socialaccount_crud import (
    SocialAccountCreateView,
    SocialAccountListView,
    SocialAccountDetailView,
    SocialAccountEditView,
    SocialAccountDeleteView,
)


# ============================================================
# LOGIN HISTORY VIEWS
# ============================================================

from account.views.loginhistory_crud import (
    LoginHistoryListView,
    LoginHistoryDetailView,
)


# ============================================================
# OTP RECORDS VIEWS
# ============================================================

from account.views.otp_crud import (
    OTPListView,
    OTPDetailView,
)


# ============================================================
# USER SESSION VIEWS
# ============================================================

from account.views.usersession_crud import (
    UserSessionListView,
    UserSessionDetailView,
    UserSessionRevokeView,
)

from account.views.session_validation import (
    SessionValidationView,
)


# =========================
# USER + PROFILE VIEWS
# =========================
from account.views.user_profile import (
    UserProfileAPIView,
    UserProfileImageAPIView,
    UserProfileImageDeleteAPIView,
    UserMeAPIView,
)

# =========================
# SOCIAL LINKS
# =========================
from account.views.user_social_link import (
    UserSocialLinkAPIView,
    UserSocialLinkUpdateAPIView,
    UserSocialLinkSetPrimaryAPIView,
    UserSocialLinkReorderAPIView,
    UserSocialLinkDeleteAPIView
)

urlpatterns = [

    # =====================================
    # AUTH ROUTES
    # =====================================
    path("auth/register/", UserRegistrationView.as_view()),
    path("auth/login/", UserLoginView.as_view()),
    path("auth/token/refresh/", UserTokenRefreshView.as_view()),
    path("auth/verify-otp/", OTPVerificationView.as_view()),
    path("auth/resend-otp/", OTPResendView.as_view()),
    path("auth/change-password/", UserChangePasswordView.as_view()),
    path("auth/forgot-password/", PasswordForgotView.as_view()),
    path("auth/reset-password/", PasswordResetView.as_view()),
    path("auth/logout/", LogoutView.as_view()),
    path("auth/logout-all/", LogoutAllView.as_view()),
    path("auth/social/login/", SocialLoginView.as_view(), name="social_login"),

    # =====================================
    # CURRENT USER
    # =====================================
    path("me/", UserMeAPIView.as_view()),
    path("auth/me/", UserProfileView.as_view()),

    # =====================================
    # USER MANAGEMENT (ADMIN)
    # =====================================
    path("accounts/users/create/", UserCreateView.as_view()),
    path("accounts/users/", UserListView.as_view()),
    path("accounts/users/<str:user_id>/", UserDetailView.as_view()),
    path("accounts/users/<str:user_id>/edit/", UserEditView.as_view()),
    path("accounts/users/<str:user_id>/status/",
         UserStatusUpdateView.as_view()),
    path("accounts/users/<str:user_id>/delete/", UserDeleteView.as_view()),

    # =====================================
    # ROLE MANAGEMENT (ADMIN)
    # =====================================
    path("accounts/roles/create/", RoleCreateView.as_view()),
    path("accounts/roles/", RoleListView.as_view()),
    path("accounts/roles/<str:role_id>/", RoleDetailView.as_view()),
    path("accounts/roles/<str:role_id>/edit/", RoleEditView.as_view()),
    path("accounts/roles/<str:role_id>/delete/", RoleDeleteView.as_view()),

    # =====================================
    # ROLE PERMISSION MANAGEMENT (ADMIN)
    # =====================================
    path("accounts/rolepermissions/create/", RolePermissionCreateView.as_view()),
    path("accounts/rolepermissions/", RolePermissionListView.as_view()),
    path("accounts/rolepermissions/<str:rolepermission_id>/", RolePermissionDetailView.as_view()),
    path("accounts/rolepermissions/<str:rolepermission_id>/delete/", RolePermissionDeleteView.as_view()),

    # =====================================
    # STATUS MANAGEMENT (ADMIN)
    # =====================================
    path("accounts/statuses/create/", StatusCreateView.as_view()),
    path("accounts/statuses/", StatusListView.as_view()),
    path("accounts/statuses/<str:userstatus_id>/", StatusDetailView.as_view()),
    path("accounts/statuses/<str:userstatus_id>/edit/", StatusEditView.as_view()),
    path("accounts/statuses/<str:userstatus_id>/delete/",
         StatusDeleteView.as_view()),

    # =====================================
    # OTP PURPOSE MANAGEMENT (ADMIN)
    # =====================================
    path("accounts/otppurposes/create/", OTPPurposeCreateView.as_view()),
    path("accounts/otppurposes/", OTPPurposeListView.as_view()),
    path("accounts/otppurposes/<str:otppurpose_id>/", OTPPurposeDetailView.as_view()),
    path("accounts/otppurposes/<str:otppurpose_id>/edit/", OTPPurposeEditView.as_view()),
    path("accounts/otppurposes/<str:otppurpose_id>/delete/", OTPPurposeDeleteView.as_view()),

    # =====================================
    # PERMISSION MANAGEMENT (ADMIN)
    # =====================================
    path("accounts/permissions/create/", PermissionCreateView.as_view()),
    path("accounts/permissions/", PermissionListView.as_view()),
    path("accounts/permissions/<str:permission_id>/", PermissionDetailView.as_view()),
    path("accounts/permissions/<str:permission_id>/edit/", PermissionEditView.as_view()),
    path("accounts/permissions/<str:permission_id>/delete/", PermissionDeleteView.as_view()),

    # =====================================
    # SOCIAL PROVIDER MANAGEMENT (ADMIN)
    # =====================================
    path("accounts/socialproviders/create/", SocialProviderCreateView.as_view()),
    path("accounts/socialproviders/", SocialProviderListView.as_view()),
    path("accounts/socialproviders/<str:socialprovider_id>/", SocialProviderDetailView.as_view()),
    path("accounts/socialproviders/<str:socialprovider_id>/edit/", SocialProviderEditView.as_view()),
    path("accounts/socialproviders/<str:socialprovider_id>/delete/", SocialProviderDeleteView.as_view()),

    # =====================================
    # SOCIAL ACCOUNT MANAGEMENT (ADMIN)
    # =====================================
    path("accounts/socialaccounts/create/", SocialAccountCreateView.as_view()),
    path("accounts/socialaccounts/", SocialAccountListView.as_view()),
    path("accounts/socialaccounts/<str:socialaccount_id>/", SocialAccountDetailView.as_view()),
    path("accounts/socialaccounts/<str:socialaccount_id>/edit/", SocialAccountEditView.as_view()),
    path("accounts/socialaccounts/<str:socialaccount_id>/delete/", SocialAccountDeleteView.as_view()),

    # =====================================
    # LOGIN HISTORY (ADMIN)
    # =====================================
    path("accounts/loginhistory/", LoginHistoryListView.as_view()),
    path("accounts/loginhistory/<str:loginhistory_id>/", LoginHistoryDetailView.as_view()),

    # =====================================
    # OTP RECORDS (ADMIN)
    # =====================================
    path("accounts/otps/", OTPListView.as_view()),
    path("accounts/otps/<str:otp_id>/", OTPDetailView.as_view()),

    # =====================================
    # USER SESSIONS (ADMIN)
    # =====================================
    path("accounts/sessions/validate/", SessionValidationView.as_view()),
    path("accounts/usersessions/", UserSessionListView.as_view()),
    path("accounts/usersessions/<str:usersession_id>/", UserSessionDetailView.as_view()),
    path("accounts/usersessions/<str:usersession_id>/revoke/", UserSessionRevokeView.as_view()),

    # =====================================
    # PROFILE (EXTENDED)
    # =====================================
    path("profile/", UserProfileAPIView.as_view()),
    path("profile/image/", UserProfileImageAPIView.as_view()),
    path("profile/image/delete/", UserProfileImageDeleteAPIView.as_view()),

    # =====================================
    # SOCIAL LINKS
    # =====================================
    path("profile/social-links/", UserSocialLinkAPIView.as_view()),
    path("profile/social-links/reorder/",
         UserSocialLinkReorderAPIView.as_view()),
    path("profile/social-links/<str:usersociallink_id>/",
         UserSocialLinkUpdateAPIView.as_view()),
    path("profile/social-links/<str:usersociallink_id>/set-primary/",
         UserSocialLinkSetPrimaryAPIView.as_view()),
    path("profile/social-links/<str:usersociallink_id>/delete/",
         UserSocialLinkDeleteAPIView.as_view()),
]
