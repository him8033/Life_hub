from django.urls import path

from travelhub.views.travelspot_views import (
    TravelSpotDetailAPIView,
    TravelSpotUpdateDeleteAPIView,
    TravelSpotNameCheckAPIView,
    TravelSpotVisitorListAPIView
)

from travelhub.views.travelspot_list import (
    TravelSpotListAPIView,
    TravelSpotListCreateAPIView
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
from travelhub.views.nearby import (
    NearbyTravelSpotsAPIView
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
    path(
        "travel-spots/<slug:slug>/nearby/",
        NearbyTravelSpotsAPIView.as_view(),
        name="nearby-travel-spots"
    ),

    # =========================
    # Admin Utilities
    # =========================
    path(
        "admin/travel-spots/check-name/",
        TravelSpotNameCheckAPIView.as_view(),
        name="travelspot-check-name"
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

    # Travelspot visitors
    path(
        "admin/travel-spots/<str:travelspot_id>/visitors/",
        TravelSpotVisitorListAPIView.as_view(),
        name="travelspot-visitors",
    ),
]
