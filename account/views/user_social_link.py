from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db import transaction

from life_hub.renderers import UserRenderer
from account.models.user_social_link import UserSocialLink
from account.serializers.user_social_link import (
    UserSocialLinkSerializer,
    UserSocialLinkReorderSerializer
)


# ============================================
# LIST + CREATE
# ============================================

class UserSocialLinkAPIView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = request.user.profile

        links = UserSocialLink.objects.filter(
            user_profile=profile,
            is_active=True
        ).order_by("position")

        serializer = UserSocialLinkSerializer(links, many=True)

        return Response({
            "message": "Social links fetched successfully",
            "data": serializer.data
        })

    def post(self, request):
        profile = request.user.profile

        serializer = UserSocialLinkSerializer(
            data=request.data,
            context={"profile": profile}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Social link added successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


# ============================================
# UPDATE
# ============================================

class UserSocialLinkUpdateAPIView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def put(self, request, usersociallink_id):
        profile = request.user.profile

        link = UserSocialLink.objects.get(
            usersociallink_id=usersociallink_id,
            user_profile=profile
        )

        serializer = UserSocialLinkSerializer(
            link,
            data=request.data,
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Social link updated successfully",
            "data": serializer.data
        })


# ============================================
# SET PRIMARY
# ============================================

class UserSocialLinkSetPrimaryAPIView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def patch(self, request, usersociallink_id):
        profile = request.user.profile

        link = UserSocialLink.objects.select_for_update().get(
            usersociallink_id=usersociallink_id,
            user_profile=profile
        )

        # Remove existing primary
        UserSocialLink.objects.filter(
            user_profile=profile,
            is_primary=True
        ).update(is_primary=False)

        # Set new primary
        link.is_primary = True
        link.save(update_fields=["is_primary"])

        return Response({
            "message": "Primary social link updated successfully"
        })


# ============================================
# REORDER
# ============================================

class UserSocialLinkReorderAPIView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def patch(self, request):
        profile = request.user.profile

        serializer = UserSocialLinkReorderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data["order"]

        links = UserSocialLink.objects.select_for_update().filter(
            user_profile=profile
        )

        if links.count() != len(data):
            return Response(
                {"message": "Mismatch in number of links"},
                status=status.HTTP_400_BAD_REQUEST
            )

        link_map = {l.usersociallink_id: l for l in links}

        for item in data:
            link = link_map.get(item["usersociallink_id"])
            if not link:
                return Response(
                    {"message": "Invalid ID"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            link.position = item["position"]

        UserSocialLink.objects.bulk_update(links, ["position"])

        return Response({
            "message": "Social links reordered successfully"
        })


# ============================================
# DELETE
# ============================================

class UserSocialLinkDeleteAPIView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def delete(self, request, usersociallink_id):
        profile = request.user.profile

        link = UserSocialLink.objects.select_for_update().get(
            usersociallink_id=usersociallink_id,
            user_profile=profile
        )

        links = UserSocialLink.objects.filter(
            user_profile=profile
        ).order_by("position")

        if links.count() <= 1:
            return Response(
                {"message": "At least one link required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        deleted_position = link.position
        was_primary = link.is_primary

        link.delete()

        # Reassign primary
        if was_primary:
            next_link = UserSocialLink.objects.filter(
                user_profile=profile
            ).order_by("position").first()

            next_link.is_primary = True
            next_link.save(update_fields=["is_primary"])

        # Reorder
        remaining = UserSocialLink.objects.filter(
            user_profile=profile,
            position__gt=deleted_position
        )

        for l in remaining:
            l.position -= 1

        UserSocialLink.objects.bulk_update(remaining, ["position"])

        return Response({
            "message": "Social link deleted successfully"
        })
