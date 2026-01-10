from django.urls import path
from .views import (
    TravelSpotListAPIView,
    TravelSpotListCreateAPIView,
    TravelSpotDetailAPIView,
    TravelSpotUpdateDeleteAPIView
)

# urlpatterns = [
#     path("", TravelSpotListCreateAPIView.as_view(),
#          name="travelspot-listcreate"),
#     path("<str:slug>/", TravelSpotDetailAPIView.as_view(),
#          name="travelspot-detail"),
# ]

urlpatterns = [
    path("travel-spots/", TravelSpotListAPIView.as_view()),
    path("travel-spots/<str:slug>/", TravelSpotDetailAPIView.as_view()),

    # Admin
    path("admin/travel-spots/", TravelSpotListCreateAPIView.as_view()),
    path("admin/travel-spots/<str:slug>/",
         TravelSpotUpdateDeleteAPIView.as_view()),
]
