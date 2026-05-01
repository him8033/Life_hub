# account/urls.py

from django.urls import path

# =========================
# AUTH VIEWS
# =========================
from account.views.user_views import (
    SendPasswordResetEmailView,
    UserChangePasswordView,
    UserPasswordResetView,
    UserRegistrationView,
    UserLoginView,
    UserTokenRefreshView,
)

# =========================
# USER + PROFILE VIEWS
# =========================
from account.views.user_profile import (
    UserProfileAPIView,
    UserProfileImageAPIView,
    UserProfileImageDeleteAPIView,
    UserMeAPIView,  # 👈 NEW (important)
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

    path("auth/change-password/", UserChangePasswordView.as_view()),
    path("auth/send-reset-password-email/",
         SendPasswordResetEmailView.as_view()),
    path("auth/reset-password/<uid>/<token>/", UserPasswordResetView.as_view()),


    # =====================================
    # CURRENT USER (IMPORTANT CHANGE)
    # =====================================
    path("me/", UserMeAPIView.as_view()),


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

    path(
        "profile/social-links/reorder/",
        UserSocialLinkReorderAPIView.as_view()
    ),

    path(
        "profile/social-links/<str:usersociallink_id>/",
        UserSocialLinkUpdateAPIView.as_view()
    ),

    path(
        "profile/social-links/<str:usersociallink_id>/set-primary/",
        UserSocialLinkSetPrimaryAPIView.as_view()
    ),

    path(
        "profile/social-links/<str:usersociallink_id>/delete/",
        UserSocialLinkDeleteAPIView.as_view()
    ),
]
