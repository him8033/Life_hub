from django.urls import path
from travelhub.views.category_views import (
    SpotCategoryListAPIView,
    SpotCategoryDetailAPIView,
    SpotCategoryListCreateAPIView,
    SpotCategoryUpdateDeleteAPIView
)

urlpatterns = [
    # Public
    path("spot-categories/", SpotCategoryListAPIView.as_view()),
    path("spot-categories/<str:slug>/", SpotCategoryDetailAPIView.as_view()),

    # Admin
    path("admin/spot-categories/", SpotCategoryListCreateAPIView.as_view()),
    path(
        "admin/spot-categories/<str:slug>/",
        SpotCategoryUpdateDeleteAPIView.as_view()
    ),
]
