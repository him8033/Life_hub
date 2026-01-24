from django.urls import path
from .views import *

urlpatterns = [
    path('countries/', CountryAPIView.as_view()),
    path('states/', StateAPIView.as_view()),
    path('districts/', DistrictAPIView.as_view()),
    path('sub-districts/', SubDistrictAPIView.as_view()),
    path('villages/', VillageAPIView.as_view()),
    path('pincodes/', PincodeAPIView.as_view()),
]
