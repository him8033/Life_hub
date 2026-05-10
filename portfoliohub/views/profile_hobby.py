from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from life_hub.renderers import UserRenderer

from portfoliohub.models.profile_snapshot import ProfileSnapshot
from portfoliohub.models.profile_hobby import ProfileHobby

from portfoliohub.serializers.profile_hobby import (
    ProfileHobbySerializer
)


# ============================================
# LIST + CREATE
# ============================================

class ProfileHobbyAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request, snapshot_id):

        snapshot = get_object_or_404(
            ProfileSnapshot,
            profile_snapshot_id=snapshot_id,
            user=request.user
        )

        hobbies = ProfileHobby.objects.filter(
            profile_snapshot=snapshot
        ).order_by("position")

        serializer = ProfileHobbySerializer(
            hobbies,
            many=True
        )

        return Response({
            "message": "Hobbies fetched successfully",
            "data": serializer.data
        })

    def post(self, request, snapshot_id):

        data = request.data.copy()
        data["profile_snapshot_id"] = snapshot_id

        serializer = ProfileHobbySerializer(
            data=data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Hobby added successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


# ============================================
# UPDATE + DELETE
# ============================================

class ProfileHobbyDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get_object(self, request, hobby_id):

        return get_object_or_404(
            ProfileHobby,
            profilehobby_id=hobby_id,
            profile_snapshot__user=request.user
        )

    def put(self, request, hobby_id):

        hobby = self.get_object(request, hobby_id)

        serializer = ProfileHobbySerializer(
            hobby,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Hobby updated successfully",
            "data": serializer.data
        })

    def delete(self, request, hobby_id):

        hobby = self.get_object(request, hobby_id)

        hobby.delete()

        return Response({
            "message": "Hobby deleted successfully"
        })


# ============================================
# REORDER
# ============================================

class ProfileHobbyReorderAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def post(self, request, snapshot_id):

        snapshot = get_object_or_404(
            ProfileSnapshot,
            profile_snapshot_id=snapshot_id,
            user=request.user
        )

        order = request.data.get("order", [])

        for index, hobby_id in enumerate(order):

            ProfileHobby.objects.filter(
                profilehobby_id=hobby_id,
                profile_snapshot=snapshot
            ).update(position=index)

        return Response({
            "message": "Hobbies reordered successfully"
        })
