from rest_framework import serializers
from travelhub.models import TravelSpot


class NearbySpotSerializer(serializers.ModelSerializer):
    distance_km = serializers.FloatField()
    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = TravelSpot
        fields = [
            "travelspot_id",
            "name",
            "slug",
            "distance_km",
            "primary_image",
        ]

    def get_primary_image(self, obj):
        image = obj.images.filter(
            is_primary=True,
            deleted_at__isnull=True
        ).first()

        if not image:
            return None

        from cloudinary.utils import cloudinary_url
        url, _ = cloudinary_url(
            image.public_id,
            width=400,
            height=300,
            crop="fill",
            quality="auto",
            fetch_format="auto"
        )
        return url
