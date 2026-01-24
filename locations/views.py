from django.shortcuts import render

# Create your views here.
from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import *
from .serializers import *

# 1. Start here


class CountryList(generics.ListAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer

# 2. Filter by country_id


class StateList(generics.ListAPIView):
    queryset = State.objects.all().order_by('name')
    serializer_class = StateSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['country_id']

# 3. Filter by state_id


class DistrictList(generics.ListAPIView):
    queryset = District.objects.all().order_by('name')
    serializer_class = DistrictSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['state_id']

# 4. Filter by district_id


class SubDistrictList(generics.ListAPIView):
    queryset = SubDistrict.objects.all().order_by('name')
    serializer_class = SubDistrictSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['district_id']

# 5. Filter by sub_district_id


class VillageList(generics.ListAPIView):
    queryset = Village.objects.all().order_by('name')
    serializer_class = VillageSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['sub_district_id']

# 6. Search by Pincode OR Filter by Village


class PincodeList(generics.ListAPIView):
    queryset = Pincode.objects.all()
    serializer_class = PincodeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['village_id']
    search_fields = ['pincode']  # Allows /api/pincodes/?search=110001
