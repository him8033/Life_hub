# travelhub/serializers/spot_image.py

from rest_framework import serializers
from travelhub.models import TravelSpot
from travelhub.models.spot_image import SpotImage
import cloudinary.uploader


class SpotImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = SpotImage
        fields = [
            "id",
            "spotimage_id",
            "image",
            "image_url",
            "caption",
            "is_primary",
            "position",
            "is_active",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "spotimage_id",
            "is_primary",
            "position",
            "created_at",
        ]

    def get_image_url(self, obj):
        from cloudinary.utils import cloudinary_url
        url, _ = cloudinary_url(
            obj.public_id,
            # width=800,
            # height=450,     # 16:9
            # crop="fill",
            quality="auto",
            fetch_format="auto"
        )
        return url

    def create(self, validated_data):
        request = self.context["request"]
        travelspot = self.context["travelspot"]

        # Upload to Cloudinary with custom folder
        upload = cloudinary.uploader.upload(
            validated_data["image"],
            folder=f"travelhub/travelspots/{travelspot.travelspot_id}/spot_images",
            resource_type="image",
            transformation=[
                # resize large images
                {"width": 1600, "height": 900, "crop": "fill", "gravity": "auto"},
                {"quality": "auto"},   # auto compression
                {"fetch_format": "auto"}  # auto WebP/AVIF
            ]
        )

        spot_image = SpotImage.objects.create(
            travelspot=travelspot,
            image=upload["public_id"],
            public_id=upload["public_id"],
            caption=validated_data.get("caption"),
            created_by=request.user,
            updated_by=request.user,
        )

        # Update TravelSpot completion status
        if travelspot.completion_status == "details":
            travelspot.completion_status = "images"
            travelspot.save(update_fields=["completion_status"])

        return spot_image


class SpotImageReplaceSerializer(serializers.Serializer):
    image = serializers.ImageField(required=True)
    caption = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError(
                "Provide at least image or caption to update."
            )
        return attrs

    def update(self, instance, validated_data):
        request = self.context["request"]

        # =========================
        # IMAGE REPLACEMENT (OPTIONAL)
        # =========================
        if "image" in validated_data:
            # Delete old image from Cloudinary
            if instance.public_id:
                cloudinary.uploader.destroy(instance.public_id)

            travelspot = instance.travelspot

            upload = cloudinary.uploader.upload(
                validated_data["image"],
                folder=f"travelhub/travelspots/{travelspot.travelspot_id}/spot_images",
                resource_type="image",
                transformation=[
                    # resize large images
                    {"width": 1600, "height": 900, "crop": "fill", "gravity": "auto"},
                    {"quality": "auto"},   # auto compression
                    {"fetch_format": "auto"}  # auto WebP/AVIF
                ]
            )

            instance.image = upload["public_id"]
            instance.public_id = upload["public_id"]

        # =========================
        # CAPTION UPDATE (OPTIONAL)
        # =========================
        if "caption" in validated_data:
            instance.caption = validated_data["caption"]

        instance.updated_by = request.user
        instance.save()

        return instance


class SpotImageReorderItemSerializer(serializers.Serializer):
    spotimage_id = serializers.CharField()
    position = serializers.IntegerField(min_value=1)


class SpotImageReorderSerializer(serializers.Serializer):
    order = SpotImageReorderItemSerializer(many=True)

    def validate(self, data):
        positions = [item["position"] for item in data["order"]]

        if len(positions) != len(set(positions)):
            raise serializers.ValidationError(
                "Duplicate positions not allowed")

        # Ensure continuous positions
        if sorted(positions) != list(range(1, len(positions) + 1)):
            raise serializers.ValidationError(
                "Positions must start from 1 and be continuous")

        return data
