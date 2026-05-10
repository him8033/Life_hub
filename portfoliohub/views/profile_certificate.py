from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from life_hub.renderers import UserRenderer
import cloudinary.uploader
from portfoliohub.models.profile_snapshot import ProfileSnapshot
from portfoliohub.models.profile_certificate import ProfileCertificate

from portfoliohub.serializers.profile_certificate import (
    ProfileCertificateSerializer
)


# ============================================
# LIST + CREATE
# ============================================

class ProfileCertificateAPIView(APIView):

    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request, snapshot_id):

        snapshot = get_object_or_404(
            ProfileSnapshot,
            profile_snapshot_id=snapshot_id,
            user=request.user
        )

        certificates = ProfileCertificate.objects.filter(
            profile_snapshot=snapshot
        ).order_by("position", "-issued_date")

        serializer = ProfileCertificateSerializer(
            certificates,
            many=True
        )

        return Response({
            "message": "Certificates fetched successfully",
            "data": serializer.data
        })

    def post(self, request, snapshot_id):

        data = request.data.copy()

        data["profile_snapshot_id"] = snapshot_id

        serializer = ProfileCertificateSerializer(
            data=data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Certificate added successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


# ============================================
# UPDATE + DELETE
# ============================================

class ProfileCertificateDetailAPIView(APIView):

    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get_object(self, request, certificate_id):

        return get_object_or_404(
            ProfileCertificate,
            profilecertificate_id=certificate_id,
            profile_snapshot__user=request.user
        )

    def put(self, request, certificate_id):

        certificate = self.get_object(
            request,
            certificate_id
        )

        serializer = ProfileCertificateSerializer(
            certificate,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Certificate updated successfully",
            "data": serializer.data
        })

    def delete(self, request, certificate_id):

        certificate = self.get_object(
            request,
            certificate_id
        )

        # DELETE CLOUDINARY IMAGE
        if certificate.public_id:
            cloudinary.uploader.destroy(certificate.public_id)

        certificate.delete()

        return Response({
            "message": "Certificate deleted successfully"
        })


# ============================================
# REORDER
# ============================================

class ProfileCertificateReorderAPIView(APIView):

    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def post(self, request, snapshot_id):

        snapshot = get_object_or_404(
            ProfileSnapshot,
            profile_snapshot_id=snapshot_id,
            user=request.user
        )

        order = request.data.get("order", [])

        for index, certificate_id in enumerate(order):

            ProfileCertificate.objects.filter(
                profilecertificate_id=certificate_id,
                profile_snapshot=snapshot
            ).update(position=index)

        return Response({
            "message": "Certificates reordered successfully"
        })
