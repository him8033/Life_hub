# travelhub/serializers/travelspot/basic_info.py

from rest_framework import serializers
from travelhub.models import TravelSpot, SpotCategory


class TravelSpotBasicInfoSerializer(serializers.ModelSerializer):
    categories = serializers.SlugRelatedField(
        slug_field="spotcategory_id",
        queryset=SpotCategory.objects.filter(deleted_at__isnull=True),
        many=True
    )

    class Meta:
        model = TravelSpot
        fields = [
            "name",
            "slug",
            "short_description",
            "categories",
        ]
