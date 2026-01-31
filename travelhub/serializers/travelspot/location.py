# travelhub/serializers/travelspot/location.py

from rest_framework import serializers
from travelhub.models import TravelSpot
from locations.models import Country, State, District, SubDistrict, Village, Pincode


class TravelSpotLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelSpot
        fields = [
            "country",
            "state",
            "district",
            "sub_district",
            "village",
            "pincode",
            "latitude",
            "longitude",
            "full_address",
        ]
