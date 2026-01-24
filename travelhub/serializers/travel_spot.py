from rest_framework import serializers
from travelhub.models import TravelSpot
from travelhub.models import SpotCategory
from travelhub.serializers.spot_category_read import SpotCategoryReadSerializer


class TravelSpotSerializer(serializers.ModelSerializer):
    # WRITE ONLY (IDs)
    categories = serializers.SlugRelatedField(
        slug_field="spotcategory_id",
        queryset=SpotCategory.objects.filter(deleted_at__isnull=True),
        many=True,
        required=False,
        write_only=True
    )

    # READ ONLY (Full Objects)
    category_details = SpotCategoryReadSerializer(
        source="categories",
        many=True,
        read_only=True
    )

    class Meta:
        model = TravelSpot
        fields = [
            "id",
            "travelspot_id",
            "name",
            "slug",
            "short_description",
            "long_description",

            "entry_fee",
            "opening_time",
            "closing_time",
            "best_time_to_visit",

            "full_address",
            "city",
            "latitude",
            "longitude",
            
            "categories",          # write
            "category_details",    # read
            
            "is_active",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
            "deleted_at",
        ]
        read_only_fields = (
            "id",
            "travelspot_id",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
            "deleted_at"
        )

    def create(self, validated_data):
        # Automatically set the logged-in user as created_by & updated_by
        request = self.context.get("request")
        validated_data["created_by"] = request.user
        validated_data["updated_by"] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Automatically set updated_by to logged-in user
        request = self.context.get("request")
        instance.updated_by = request.user
        return super().update(instance, validated_data)
