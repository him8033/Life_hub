from django.urls import path
from travelhub.views.category_views import (
    SpotCategoryListAPIView,
    SpotCategoryListCreateAPIView,
    SpotCategoryUpdateDeleteAPIView,
    SpotCategoryCheckAPIView
)

urlpatterns = [
    # Public
    path("spot-categories/", SpotCategoryListAPIView.as_view()),

    # Admin Utilities
    path(
        "admin/spot-categories/check-name/",
        SpotCategoryCheckAPIView.as_view(),
        name="spotcategory-check-name"
    ),

    # Admin
    path("admin/spot-categories/", SpotCategoryListCreateAPIView.as_view()),
    path(
        "admin/spot-categories/<str:slug>/",
        SpotCategoryUpdateDeleteAPIView.as_view()
    ),
]
