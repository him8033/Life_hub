from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from account.models import OTPPurpose

from account.serializers.otppurpose_crud import (
    OTPPurposeCreateSerializer,
    OTPPurposeEditSerializer,
    OTPPurposeListSerializer,
    OTPPurposeDetailSerializer,
)

from account.renderers import UserRenderer

from account.pagination import UserAdminPagination


# ============================================================
# PERMISSION HELPER
# ============================================================


def check_permission(
    user,
    permission_slug,
):
    """
    Check whether the user has the requested permission.

    Converts:
        otppurpose.list
        otppurpose.view
        otppurpose.create
        otppurpose.update
        otppurpose.delete

    into:
        module + action

    Returns:
        Response if permission denied
        None if permission is granted
    """

    try:
        module, action = permission_slug.split(
            ".",
            1,
        )
    except ValueError:

        return Response(
            {
                "non_field_errors": [
                    "Invalid permission format."
                ]
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    from account.services.permission_service import PermissionService

    has_permission = (
        PermissionService.check_module_permission(
            user,
            module,
            action,
        )
    )

    if not has_permission:

        return Response(
            {
                "non_field_errors": [
                    "You do not have permission to perform this action."
                ]
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    return None


# ============================================================
# OTP PURPOSE CREATE (ADMIN)
# ============================================================


class OTPPurposeCreateView(APIView):
    """
    Admin API for creating new OTP purposes.
    """

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # ----------------------------------------------------
        # Permission
        # ----------------------------------------------------

        permission_error = check_permission(
            request.user,
            "otppurpose.create",
        )

        if permission_error:
            return permission_error

        # ----------------------------------------------------
        # Validate and create OTP purpose
        # ----------------------------------------------------

        serializer = OTPPurposeCreateSerializer(
            data=request.data
        )

        if not serializer.is_valid():
            return Response(
                {
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ----------------------------------------------------
        # Create OTP purpose and return response
        # ----------------------------------------------------

        otppurpose = serializer.save()

        return Response(
            {
                "message": "OTP purpose created successfully",
                "data": OTPPurposeDetailSerializer(otppurpose).data
            },
            status=status.HTTP_201_CREATED,
        )


# ============================================================
# OTP PURPOSE LIST
# ============================================================


class OTPPurposeListView(APIView):
    """
    Admin API for listing OTP purposes.

    Supports:
    - Search
    - Active status filter
    - Ordering
    - Pagination
    """

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    pagination_class = UserAdminPagination

    def get(self, request):
        # ----------------------------------------------------
        # Permission
        # ----------------------------------------------------

        permission_error = check_permission(
            request.user,
            "otppurpose.list",
        )

        if permission_error:
            return permission_error

        # ----------------------------------------------------
        # Base queryset
        # ----------------------------------------------------

        otppurposes = OTPPurpose.objects.all()

        # ----------------------------------------------------
        # Search
        # ----------------------------------------------------

        search = request.query_params.get("search", "")
        if search:
            otppurposes = otppurposes.filter(
                Q(name__icontains=search) |
                Q(slug__icontains=search) |
                Q(description__icontains=search)
            )

        # ----------------------------------------------------
        # Filter by active status
        # ----------------------------------------------------

        is_active = request.query_params.get("is_active")
        if is_active and is_active.strip():
            otppurposes = otppurposes.filter(is_active=is_active.lower() == "true")

        # ----------------------------------------------------
        # Ordering
        # ----------------------------------------------------

        ordering = request.query_params.get("ordering", "name")
        otppurposes = otppurposes.order_by(ordering)

        # ----------------------------------------------------
        # Pagination
        # ----------------------------------------------------

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(otppurposes, request)

        if page is not None:
            serializer = OTPPurposeListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = OTPPurposeListSerializer(otppurposes, many=True)
        return Response(
            {
                "data": serializer.data,
                "message": "OTP purposes retrieved successfully"
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# OTP PURPOSE DETAIL
# ============================================================


class OTPPurposeDetailView(APIView):
    """
    Admin API for retrieving OTP purpose details.
    """

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request, otppurpose_id):
        # ----------------------------------------------------
        # Permission
        # ----------------------------------------------------

        permission_error = check_permission(
            request.user,
            "otppurpose.view",
        )

        if permission_error:
            return permission_error

        # ----------------------------------------------------
        # Get OTP purpose
        # ----------------------------------------------------

        otppurpose = get_object_or_404(OTPPurpose, otppurpose_id=otppurpose_id)

        # ----------------------------------------------------
        # Return response
        # ----------------------------------------------------

        serializer = OTPPurposeDetailSerializer(otppurpose)

        return Response(
            {
                "data": serializer.data,
                "message": "OTP purpose retrieved successfully"
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# OTP PURPOSE EDIT
# ============================================================


class OTPPurposeEditView(APIView):
    """
    Admin API for updating an OTP purpose.
    """

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def put(self, request, otppurpose_id):
        # ----------------------------------------------------
        # Permission
        # ----------------------------------------------------

        permission_error = check_permission(
            request.user,
            "otppurpose.update",
        )

        if permission_error:
            return permission_error

        # ----------------------------------------------------
        # Get OTP purpose
        # ----------------------------------------------------

        otppurpose = get_object_or_404(OTPPurpose, otppurpose_id=otppurpose_id)

        # ----------------------------------------------------
        # Validate and update OTP purpose
        # ----------------------------------------------------

        serializer = OTPPurposeEditSerializer(
            otppurpose,
            data=request.data,
            partial=True
        )

        if not serializer.is_valid():
            return Response(
                {
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ----------------------------------------------------
        # Update OTP purpose and return response
        # ----------------------------------------------------

        otppurpose = serializer.save()

        return Response(
            {
                "message": "OTP purpose updated successfully",
                "data": OTPPurposeDetailSerializer(otppurpose).data
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# OTP PURPOSE DELETE
# ============================================================


class OTPPurposeDeleteView(APIView):
    """
    Admin API for deleting an OTP purpose.
    Performs permanent delete with usage check.
    """

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def delete(self, request, otppurpose_id):
        # ----------------------------------------------------
        # Permission
        # ----------------------------------------------------

        permission_error = check_permission(
            request.user,
            "otppurpose.delete",
        )

        if permission_error:
            return permission_error

        # ----------------------------------------------------
        # Get OTP purpose
        # ----------------------------------------------------

        otppurpose = get_object_or_404(OTPPurpose, otppurpose_id=otppurpose_id)

        # ----------------------------------------------------
        # Check if OTP purpose is in use
        # ----------------------------------------------------

        from account.models import OTP

        otp_count = OTP.objects.filter(purpose=otppurpose).count()
        if otp_count > 0:
            return Response(
                {
                    "non_field_errors": [
                        f"Cannot delete OTP purpose. It is currently used in {otp_count} OTP record(s)."
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ----------------------------------------------------
        # Delete OTP purpose
        # ----------------------------------------------------

        otppurpose.delete()

        return Response(
            {
                "message": "OTP purpose deleted successfully."
            },
            status=status.HTTP_200_OK,
        )
