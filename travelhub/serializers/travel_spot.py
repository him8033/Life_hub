from rest_framework import serializers

from travelhub.models import TravelSpot, SpotCategory
from travelhub.serializers.spot_category_read import SpotCategoryReadSerializer

from locations.models import (
    Country,
    State,
    District,
    SubDistrict,
    Village,
    Pincode
)


class TravelSpotSerializer(serializers.ModelSerializer):
    # -------------------------
    # CATEGORY HANDLING
    # -------------------------

    # WRITE ONLY → Accept spotcategory_id list
    categories = serializers.SlugRelatedField(
        slug_field="spotcategory_id",
        queryset=SpotCategory.objects.filter(deleted_at__isnull=True),
        many=True,
        required=False,
        write_only=True
    )

    # READ ONLY → Full category objects
    category_details = SpotCategoryReadSerializer(
        source="categories",
        many=True,
        read_only=True
    )

    # -------------------------
    # LOCATION (WRITE)
    # -------------------------

    country = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all(),
        required=False,
        allow_null=True
    )
    state = serializers.PrimaryKeyRelatedField(
        queryset=State.objects.all(),
        required=False,
        allow_null=True
    )
    district = serializers.PrimaryKeyRelatedField(
        queryset=District.objects.all(),
        required=False,
        allow_null=True
    )
    sub_district = serializers.PrimaryKeyRelatedField(
        queryset=SubDistrict.objects.all(),
        required=False,
        allow_null=True
    )
    village = serializers.PrimaryKeyRelatedField(
        queryset=Village.objects.all(),
        required=False,
        allow_null=True
    )
    pincode = serializers.PrimaryKeyRelatedField(
        queryset=Pincode.objects.all(),
        required=False,
        allow_null=True
    )

    # -------------------------
    # LOCATION (READ)
    # -------------------------

    location = serializers.SerializerMethodField(read_only=True)

    def get_location(self, obj):
        return {
            "country": obj.country.name if obj.country else None,
            "state": obj.state.name if obj.state else None,
            "district": obj.district.name if obj.district else None,
            "sub_district": obj.sub_district.name if obj.sub_district else None,
            "village": obj.village.name if obj.village else None,
            "zipcode": obj.pincode.pincode if obj.pincode else None,
        }

    # -------------------------
    # Primary Image (READ)
    # -------------------------

    primary_image = serializers.SerializerMethodField(read_only=True)

    def get_primary_image(self, obj):
        image = (
            obj.images
            .filter(
                is_primary=True,
                is_active=True,
                deleted_at__isnull=True
            )
            .only("spotimage_id", "image", "caption")
            .first()
        )

        if not image:
            return None

        return {
            "spotimage_id": image.spotimage_id,
            "image": image.image.url if hasattr(image.image, "url") else str(image.image),
            "caption": image.caption,
        }

    # -------------------------
    # META
    # -------------------------

    class Meta:
        model = TravelSpot
        fields = [
            "id",
            "travelspot_id",

            # Basic Info
            "name",
            "slug",
            "short_description",
            "long_description",

            # Primary Image (LISTING PREVIEW)
            "primary_image",

            # Categories
            "categories",         # WRITE
            "category_details",   # READ

            # Location
            "country",
            "state",
            "district",
            "sub_district",
            "village",
            "pincode",
            "location",          # READ ONLY aggregated view
            "full_address",
            "latitude",
            "longitude",

            # Tourist Info
            "entry_fee",
            "opening_time",
            "closing_time",
            "best_time_to_visit",
            "view_count",

            # Form Progress Status
            "completion_status",
            "is_ready_for_review",

            # Status & Audit
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
            "view_count",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
            "deleted_at",
        )

    # -------------------------
    # CREATE
    # -------------------------

    def create(self, validated_data):
        categories = validated_data.pop("categories", [])
        request = self.context.get("request")

        validated_data["created_by"] = request.user
        validated_data["updated_by"] = request.user

        travel_spot = super().create(validated_data)

        if categories:
            travel_spot.categories.set(categories)

        return travel_spot

    # -------------------------
    # UPDATE
    # -------------------------

    def update(self, instance, validated_data):
        categories = validated_data.pop("categories", None)
        request = self.context.get("request")

        instance.updated_by = request.user
        travel_spot = super().update(instance, validated_data)

        if categories is not None:
            travel_spot.categories.set(categories)

        return travel_spot
