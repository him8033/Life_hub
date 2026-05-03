from django.urls import path
from portfoliohub.views.profile_snapshot import (
    ProfileSnapshotAPIView,
    ProfileSnapshotDetailAPIView,
    ProfileSnapshotDuplicateAPIView
)
from portfoliohub.views.profile_basic_info import (
    ProfileBasicInfoAPIView
)
from portfoliohub.views.profile_social_link import (
    ProfileSocialLinkAPIView,
    ProfileSocialLinkDetailAPIView,
    ProfileSocialLinkReorderAPIView
)
from portfoliohub.views.profile_education import (
    ProfileEducationAPIView,
    ProfileEducationDetailAPIView,
    ProfileEducationReorderAPIView
)

urlpatterns = [
    # Snapshot Routes
    path("", ProfileSnapshotAPIView.as_view()),
    path("<str:snapshot_id>/",
         ProfileSnapshotDetailAPIView.as_view()),
    path("<str:snapshot_id>/duplicate/",
         ProfileSnapshotDuplicateAPIView.as_view()),

    # Profile Basic Info Route
    path("<str:snapshot_id>/basic-info/",
         ProfileBasicInfoAPIView.as_view()),

    # Profile Social Link Routes
    path("<str:snapshot_id>/social-links/",
         ProfileSocialLinkAPIView.as_view()),
    path("social-links/<str:link_id>/", ProfileSocialLinkDetailAPIView.as_view()),
    path("<str:snapshot_id>/social-links/reorder/",
         ProfileSocialLinkReorderAPIView.as_view()),

    #  Profile Education Routes
    path("<str:snapshot_id>/educations/", ProfileEducationAPIView.as_view()),
    path("educations/<str:edu_id>/", ProfileEducationDetailAPIView.as_view()),
    path("<str:snapshot_id>/educations/reorder/",
         ProfileEducationReorderAPIView.as_view()),
]
