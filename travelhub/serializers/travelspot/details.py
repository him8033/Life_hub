# travelhub/serializers/travelspot/details.py

from rest_framework import serializers
from travelhub.models import TravelSpot, SpotCategory


class TravelSpotDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelSpot
        fields = [
            "long_description",
            "entry_fee",
            "opening_time",
            "closing_time",
            "best_time_to_visit",
        ]
