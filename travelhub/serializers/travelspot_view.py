# travelhub/serializers/travelspot_view.py

from rest_framework import serializers
from travelhub.models.travelspot_view import TravelSpotView


class TravelSpotViewSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = TravelSpotView
        fields = [
            "id",
            "travelspot",
            "user",
            "user_email",
            "ip_address",
            "viewed_at",
        ]
