from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from life_hub.renderers import UserRenderer
from account.serializers.user_profile import (
    UserProfileSerializer,
    UserProfileImageReplaceSerializer
)
from account.serializers.user_me import *

import cloudinary.uploader


# ============================================
# PROFILE GET + UPDATE
# ============================================

class UserProfileAPIView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = request.user.profile

        serializer = UserProfileSerializer(profile)

        return Response({
            "message": "Profile fetched successfully",
            "data": serializer.data
        })

    def put(self, request):
        profile = request.user.profile

        serializer = UserProfileSerializer(
            profile,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Profile updated successfully",
            "data": serializer.data
        })


# ============================================
# PROFILE IMAGE UPLOAD / REPLACE
# ============================================

class UserProfileImageAPIView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        profile = request.user.profile

        serializer = UserProfileImageReplaceSerializer(
            profile,
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Profile image uploaded successfully"
        }, status=status.HTTP_200_OK)


# ============================================
# PROFILE IMAGE DELETE
# ============================================

class UserProfileImageDeleteAPIView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        profile = request.user.profile

        if not profile.public_id:
            return Response(
                {"message": "No image to delete"},
                status=status.HTTP_400_BAD_REQUEST
            )

        cloudinary.uploader.destroy(profile.public_id)

        profile.profile_image = None
        profile.public_id = None
        profile.save()

        return Response({
            "message": "Profile image deleted successfully"
        }, status=status.HTTP_200_OK)


# ============================================
#  FULL USER PROFILE DETAILS
# ============================================

class UserMeAPIView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)

        serializer = UserMeSerializer(profile)

        return Response({
            "message": "User data fetched successfully",
            "data": serializer.data
        })
