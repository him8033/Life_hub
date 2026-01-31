from django.urls import path

from travelhub.views.travelspot_views import (
    TravelSpotListAPIView,
    TravelSpotListCreateAPIView,
    TravelSpotDetailAPIView,
    TravelSpotUpdateDeleteAPIView,
)

from travelhub.views.travelspot_steps.basic_info import (
    TravelSpotBasicInfoAPIView,
)
from travelhub.views.travelspot_steps.location import (
    TravelSpotLocationAPIView,
)
from travelhub.views.travelspot_steps.details import (
    TravelSpotDetailsAPIView,
)
from travelhub.views.travelspot_steps.submit import (
    TravelSpotSubmitAPIView,
)

urlpatterns = [
    # =========================
    # Public APIs
    # =========================
    path(
        "travel-spots/",
        TravelSpotListAPIView.as_view(),
        name="travelspot-list",
    ),
    path(
        "travel-spots/<str:slug>/",
        TravelSpotDetailAPIView.as_view(),
        name="travelspot-detail",
    ),

    # =========================
    # Admin CRUD (Internal Use)
    # =========================
    path(
        "admin/travel-spots/",
        TravelSpotListCreateAPIView.as_view(),
        name="admin-travelspot-list-create",
    ),
    path(
        "admin/travel-spots/<str:travelspot_id>/",
        TravelSpotUpdateDeleteAPIView.as_view(),
        name="admin-travelspot-update-delete",
    ),

    # =========================
    # Step-based Creation APIs
    # =========================
    path(
        "admin/travel-spots/steps/basic-info/",
        TravelSpotBasicInfoAPIView.as_view(),
        name="travelspot-step-basic-info",
    ),
    path(
        "admin/travel-spots/<str:travelspot_id>/steps/basic-info/",
        TravelSpotBasicInfoAPIView.as_view(),
        name="travelspot-step-basic-update",
    ),
    path(
        "admin/travel-spots/<str:travelspot_id>/steps/location/",
        TravelSpotLocationAPIView.as_view(),
        name="travelspot-step-location",
    ),
    path(
        "admin/travel-spots/<str:travelspot_id>/steps/details/",
        TravelSpotDetailsAPIView.as_view(),
        name="travelspot-step-details",
    ),
    path(
        "admin/travel-spots/<str:travelspot_id>/steps/submit/",
        TravelSpotSubmitAPIView.as_view(),
        name="travelspot-step-submit",
    ),
]
