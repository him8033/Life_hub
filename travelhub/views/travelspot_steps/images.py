# travelhub/views/travelspot_steps/images.py

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from life_hub.renderers import UserRenderer
from travelhub.models import TravelSpot
from travelhub.models.spot_image import SpotImage
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import transaction
from django.utils import timezone
import cloudinary.uploader
from travelhub.serializers.spot_image import (
    SpotImageSerializer,
    SpotImageReplaceSerializer,
    SpotImageReorderSerializer
)


class TravelSpotImageAPIView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request, travelspot_id):
        spot = TravelSpot.objects.get(
            travelspot_id=travelspot_id,
            deleted_at__isnull=True
        )

        images = SpotImage.objects.filter(
            travelspot=spot,
            deleted_at__isnull=True,
            is_active=True
        ).order_by("position")

        serializer = SpotImageSerializer(images, many=True)
        return Response({
            "message": "Images fetched successfully",
            "data": serializer.data
        })

    def post(self, request, travelspot_id):
        spot = TravelSpot.objects.get(
            travelspot_id=travelspot_id,
            deleted_at__isnull=True
        )

        serializer = SpotImageSerializer(
            data=request.data,
            context={
                "request": request,
                "travelspot": spot
            }
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Image uploaded successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


class SpotImageReplaceAPIView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # REQUIRED

    def put(self, request, spotimage_id):
        image_obj = SpotImage.objects.get(
            spotimage_id=spotimage_id,
            deleted_at__isnull=True
        )

        serializer = SpotImageReplaceSerializer(
            image_obj,
            data=request.data,
            context={"request": request},
            partial=True  # allow caption-only update
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Image replaced successfully",
            "data": {
                "spotimage_id": image_obj.spotimage_id,
                "is_primary": image_obj.is_primary,
                "position": image_obj.position
            }
        }, status=status.HTTP_200_OK)


class SpotImageSetPrimaryAPIView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def patch(self, request, spotimage_id):
        image_obj = SpotImage.objects.select_for_update().get(
            spotimage_id=spotimage_id,
            deleted_at__isnull=True
        )

        travelspot = image_obj.travelspot

        # Remove existing primary
        SpotImage.objects.filter(
            travelspot=travelspot,
            is_primary=True,
            deleted_at__isnull=True
        ).update(is_primary=False)

        # Set new primary
        image_obj.is_primary = True
        image_obj.updated_by = request.user
        image_obj.save(update_fields=["is_primary", "updated_by"])

        return Response({
            "message": "Primary image updated successfully",
            "data": {
                "spotimage_id": image_obj.spotimage_id,
                "travelspot_id": travelspot.travelspot_id
            }
        }, status=status.HTTP_200_OK)


class SpotImageReorderAPIView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def patch(self, request, travelspot_id):
        serializer = SpotImageReorderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        images_data = serializer.validated_data["order"]

        images = SpotImage.objects.select_for_update().filter(
            travelspot__travelspot_id=travelspot_id,
            deleted_at__isnull=True
        )

        if images.count() != len(images_data):
            return Response({"message": "Image count mismatch"}, status=400)

        image_map = {img.spotimage_id: img for img in images}

        for item in images_data:
            image = image_map.get(item["spotimage_id"])
            if not image:
                return Response({"message": "Invalid image ID"}, status=400)

            image.position = item["position"]
            image.updated_by = request.user

        SpotImage.objects.bulk_update(images, ["position", "updated_by"])

        return Response({"message": "Images reordered successfully"})


class SpotImageDeleteAPIView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def delete(self, request, spotimage_id):
        image = SpotImage.objects.select_for_update().get(
            spotimage_id=spotimage_id,
            deleted_at__isnull=True
        )

        travelspot = image.travelspot

        images = SpotImage.objects.filter(
            travelspot=travelspot
        ).order_by("position")

        if images.count() <= 1:
            return Response(
                {"message": "At least one image is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Delete from Cloudinary
        if image.public_id:
            cloudinary.uploader.destroy(image.public_id)

        deleted_position = image.position
        was_primary = image.is_primary

        image.delete()

        # # Soft delete
        # image.deleted_at = timezone.now()
        # image.is_active = False
        # image.is_primary = False
        # image.updated_by = request.user
        # image.save()

        # Reassign primary if needed
        if was_primary:
            next_image = SpotImage.objects.filter(
                travelspot=travelspot,
                deleted_at__isnull=True
            ).order_by("position").first()
            next_image.is_primary = True
            next_image.updated_by = request.user
            next_image.save(update_fields=["is_primary", "updated_by"])

        # Reorder remaining images
        remaining = SpotImage.objects.filter(
            travelspot=travelspot,
            deleted_at__isnull=True,
            position__gt=deleted_position
        )

        for img in remaining:
            img.position -= 1
            img.save(update_fields=["position"])

        return Response({
            "message": "Image deleted successfully"
        }, status=status.HTTP_200_OK)
