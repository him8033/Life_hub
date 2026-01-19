from django.urls import path
from travelhub.views.travelspot_views import (
    TravelSpotListAPIView,
    TravelSpotListCreateAPIView,
    TravelSpotDetailAPIView,
    TravelSpotUpdateDeleteAPIView
)

urlpatterns = [
    path("travel-spots/", TravelSpotListAPIView.as_view()),
    path("travel-spots/<str:slug>/", TravelSpotDetailAPIView.as_view()),

    # Admin
    path("admin/travel-spots/", TravelSpotListCreateAPIView.as_view()),
    path("admin/travel-spots/<str:slug>/",
         TravelSpotUpdateDeleteAPIView.as_view()),
]
