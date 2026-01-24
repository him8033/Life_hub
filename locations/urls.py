from django.urls import path
from .views import *

urlpatterns = [
    path('countries/', CountryList.as_view(), name='country-list'),
    path('states/', StateList.as_view(), name='state-list'),
    path('districts/', DistrictList.as_view(), name='district-list'),
    path('sub-districts/', SubDistrictList.as_view(), name='sub-district-list'),
    path('villages/', VillageList.as_view(), name='village-list'),
    path('pincodes/', PincodeList.as_view(), name='pincode-list'),
]
