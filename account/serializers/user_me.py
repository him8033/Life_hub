from rest_framework import serializers
from account.models.user_profile import UserProfile
from account.models.user_social_link import UserSocialLink
from cloudinary.utils import cloudinary_url

from locations.models import (
    Country,
    State,
    District,
    SubDistrict,
    Village,
    Pincode
)


# =========================
# SOCIAL LINKS (READ)
# =========================
class UserSocialLinkReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSocialLink
        fields = [
            "usersociallink_id",
            "platform_name",
            "url",
            "is_primary",
            "position",
        ]


# =========================
# MAIN /me SERIALIZER
# =========================
class UserMeSerializer(serializers.ModelSerializer):

    # -------------------------
    # USER INFO (READ ONLY)
    # -------------------------
    user = serializers.SerializerMethodField(read_only=True)

    def get_user(self, obj):
        user = obj.user
        return {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.full_name,
            "role": user.role,
            "is_verified": user.is_verified,
        }

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
    # PROFILE IMAGE
    # -------------------------
    profile_image_url = serializers.SerializerMethodField(read_only=True)

    def get_profile_image_url(self, obj):
        if not obj.public_id:
            return None

        url, _ = cloudinary_url(
            obj.public_id,
            width=300,
            height=300,
            crop="fill",
            gravity="face",
            quality="auto",
            fetch_format="auto"
        )
        return url

    # -------------------------
    # SOCIAL LINKS
    # -------------------------
    social_links = serializers.SerializerMethodField(read_only=True)

    def get_social_links(self, obj):
        links = (
            obj.social_links
            .filter(is_active=True)
            .order_by("position")
        )
        return UserSocialLinkReadSerializer(links, many=True).data

    # -------------------------
    # META
    # -------------------------
    class Meta:
        model = UserProfile
        fields = [
            "profile_id",

            # user
            "user",

            # personal
            "phone_number",
            "headline",
            "bio",
            "date_of_birth",

            # image
            "profile_image_url",

            # location (WRITE)
            "country",
            "state",
            "district",
            "sub_district",
            "village",
            "pincode",

            # location (READ)
            "location",
            "full_address",

            # social
            "social_links",
        ]

        read_only_fields = [
            "profile_id",
            "user",
            "profile_image_url",
            "location",
            "social_links",
        ]
    