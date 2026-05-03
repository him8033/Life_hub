from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404

from life_hub.renderers import UserRenderer
from portfoliohub.models.profile_social_link import ProfileSocialLink
from portfoliohub.models.profile_snapshot import ProfileSnapshot
from portfoliohub.serializers.profile_social_link import ProfileSocialLinkSerializer


# ============================================
# LIST + CREATE
# ============================================

class ProfileSocialLinkAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request, snapshot_id):
        snapshot = get_object_or_404(
            ProfileSnapshot,
            profile_snapshot_id=snapshot_id,
            user=request.user
        )

        links = ProfileSocialLink.objects.filter(
            profile_snapshot=snapshot
        ).order_by("position")

        serializer = ProfileSocialLinkSerializer(links, many=True)

        return Response({
            "message": "Social links fetched successfully",
            "data": serializer.data
        })

    def post(self, request, snapshot_id):
        data = request.data.copy()
        data["profile_snapshot_id"] = snapshot_id

        serializer = ProfileSocialLinkSerializer(
            data=data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Social link created successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


# ============================================
# UPDATE + DELETE
# ============================================

class ProfileSocialLinkDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get_object(self, request, link_id):
        return get_object_or_404(
            ProfileSocialLink,
            profilesociallink_id=link_id,
            profile_snapshot__user=request.user
        )

    def put(self, request, link_id):
        link = self.get_object(request, link_id)

        serializer = ProfileSocialLinkSerializer(
            link,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Social link updated successfully",
            "data": serializer.data
        })

    def delete(self, request, link_id):
        link = self.get_object(request, link_id)
        link.delete()

        return Response({
            "message": "Social link deleted successfully"
        }, status=status.HTTP_200_OK)


# ============================================
# REORDER (IMPORTANT UX FEATURE)
# ============================================

class ProfileSocialLinkReorderAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def post(self, request, snapshot_id):
        snapshot = get_object_or_404(
            ProfileSnapshot,
            profile_snapshot_id=snapshot_id,
            user=request.user
        )

        order = request.data.get("order", [])

        for index, link_id in enumerate(order):
            ProfileSocialLink.objects.filter(
                profilesociallink_id=link_id,
                profile_snapshot=snapshot
            ).update(position=index)

        return Response({
            "message": "Social links reordered successfully"
        })
