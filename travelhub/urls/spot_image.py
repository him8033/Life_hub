from django.urls import path

from travelhub.views.travelspot_steps.images import (
    TravelSpotImageAPIView,
    SpotImageReplaceAPIView,
    SpotImageSetPrimaryAPIView,
    SpotImageReorderAPIView,
    SpotImageDeleteAPIView
)


urlpatterns = [
    path(
        "admin/travel-spots/<str:travelspot_id>/images/",
        TravelSpotImageAPIView.as_view(),
        name="travelspot-images"
    ),

    path(
        "admin/travel-spots/images/<str:spotimage_id>/replace/",
        SpotImageReplaceAPIView.as_view(),
        name="spotimage-replace"
    ),

    path(
        "admin/travel-spots/images/<str:spotimage_id>/set-primary/",
        SpotImageSetPrimaryAPIView.as_view(),
        name="spotimage-set-primary"
    ),

    path(
        "admin/travel-spots/<str:travelspot_id>/images/reorder/",
        SpotImageReorderAPIView.as_view(),
        name="spotimage-reorder"
    ),

    path(
        "admin/travel-spots/images/<str:spotimage_id>/delete/",
        SpotImageDeleteAPIView.as_view(),
        name="spotimage-delete"
    ),

]
