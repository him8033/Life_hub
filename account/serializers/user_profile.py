# account/serializers/user_profile.py

from rest_framework import serializers
from account.models.user_profile import UserProfile
import cloudinary.uploader


# ============================================
# PROFILE SERIALIZER
# ============================================

class UserProfileSerializer(serializers.ModelSerializer):

    # =========================
    # USER FIELDS
    # =========================
    first_name = serializers.CharField(
        source="user.first_name",
        required=False
    )

    last_name = serializers.CharField(
        source="user.last_name",
        required=False
    )

    email = serializers.EmailField(
        source="user.email",
        required=False
    )

    # =========================
    # IMAGE URL
    # =========================
    profile_image_url = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [

            # USER
            "first_name",
            "last_name",
            "email",

            # PROFILE
            "profile_id",
            "profile_image",
            "profile_image_url",
            "phone_number",
            "headline",
            "bio",
            "date_of_birth",

            # LOCATION
            "country",
            "state",
            "district",
            "sub_district",
            "village",
            "pincode",
            "full_address",

            # META
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "profile_id",
            "created_at",
            "updated_at",
        ]

    # =========================
    # PROFILE IMAGE URL
    # =========================
    def get_profile_image_url(self, obj):

        from cloudinary.utils import cloudinary_url

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

    # =========================
    # UPDATE USER + PROFILE
    # =========================
    def update(self, instance, validated_data):

        # Extract user data
        user_data = validated_data.pop("user", {})

        # =========================
        # UPDATE USER MODEL
        # =========================
        user = instance.user

        if "first_name" in user_data:
            user.first_name = user_data["first_name"]

        if "last_name" in user_data:
            user.last_name = user_data["last_name"]

        if "email" in user_data:
            user.email = user_data["email"]

        user.save()

        # =========================
        # UPDATE PROFILE MODEL
        # =========================
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance


# ============================================
# PROFILE IMAGE REPLACE SERIALIZER
# ============================================

class UserProfileImageReplaceSerializer(serializers.Serializer):

    image = serializers.ImageField(required=True)

    def update(self, instance, validated_data):

        # Delete old image
        if instance.public_id:
            cloudinary.uploader.destroy(instance.public_id)

        upload = cloudinary.uploader.upload(
            validated_data["image"],
            folder=f"lifehub/users/{instance.profile_id}/profile",
            resource_type="image",
            transformation=[
                {
                    "width": 500,
                    "height": 500,
                    "crop": "fill",
                    "gravity": "face"
                },
                {"quality": "auto"},
                {"fetch_format": "auto"},
            ]
        )

        instance.profile_image = upload["public_id"]
        instance.public_id = upload["public_id"]

        instance.save()

        return instance
