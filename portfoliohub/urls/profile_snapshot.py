from django.urls import path
from portfoliohub.views.profile_snapshot import (
    ProfileSnapshotAPIView,
    ProfileSnapshotDetailAPIView,
    ProfileSnapshotDuplicateAPIView
)

urlpatterns = [
    path("portfoliohub/", ProfileSnapshotAPIView.as_view()),
    path("portfoliohub/<str:snapshot_id>/",
         ProfileSnapshotDetailAPIView.as_view()),
    path("portfoliohub/<str:snapshot_id>/duplicate/",
         ProfileSnapshotDuplicateAPIView.as_view()),
]
