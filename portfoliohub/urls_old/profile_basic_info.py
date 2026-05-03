from django.urls import path
from portfoliohub.views.profile_basic_info import (
    ProfileBasicInfoAPIView
)

urlpatterns = [
    path("portfoliohub/<str:snapshot_id>/basic-info/", ProfileBasicInfoAPIView.as_view()),
]
