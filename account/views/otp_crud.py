from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from account.models import OTP

from account.serializers.otp_crud import (
    OTPListSerializer,
    OTPDetailSerializer,
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
# OTP LIST
# ============================================================


class OTPListView(APIView):
    """
    Admin API for listing OTP records.

    Supports:
    - Search by user email, purpose
    - Filter by used status, purpose
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
            "otp.list",
        )

        if permission_error:
            return permission_error

        # ----------------------------------------------------
        # Base queryset
        # ----------------------------------------------------

        otps = OTP.objects.select_related('user', 'purpose').all()

        # ----------------------------------------------------
        # Search
        # ----------------------------------------------------

        search = request.query_params.get("search", "")
        if search:
            otps = otps.filter(
                Q(user__email__icontains=search) |
                Q(purpose__name__icontains=search) |
                Q(purpose__slug__icontains=search) |
                Q(requested_ip__icontains=search)
            )

        # ----------------------------------------------------
        # Filter by used status
        # ----------------------------------------------------

        is_used = request.query_params.get("is_used")
        if is_used and is_used.strip():
            otps = otps.filter(is_used=is_used.lower() == "true")

        # ----------------------------------------------------
        # Filter by purpose
        # ----------------------------------------------------

        purpose = request.query_params.get("purpose")
        if purpose and purpose.strip():
            otps = otps.filter(purpose__slug=purpose.strip())

        # ----------------------------------------------------
        # Ordering
        # ----------------------------------------------------

        ordering = request.query_params.get("ordering", "-created_at")
        otps = otps.order_by(ordering)

        # ----------------------------------------------------
        # Pagination
        # ----------------------------------------------------

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(otps, request)

        if page is not None:
            serializer = OTPListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = OTPListSerializer(otps, many=True)
        return Response(
            {
                "data": serializer.data,
                "message": "OTP records retrieved successfully"
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# OTP DETAIL
# ============================================================


class OTPDetailView(APIView):
    """
    Admin API for retrieving OTP details.
    """

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request, otp_id):
        # ----------------------------------------------------
        # Permission
        # ----------------------------------------------------

        permission_error = check_permission(
            request.user,
            "otp.view",
        )

        if permission_error:
            return permission_error

        # ----------------------------------------------------
        # Get OTP
        # ----------------------------------------------------

        otp = get_object_or_404(
            OTP.objects.select_related('user', 'purpose'),
            otp_id=otp_id
        )

        # ----------------------------------------------------
        # Return response
        # ----------------------------------------------------

        serializer = OTPDetailSerializer(otp)

        return Response(
            {
                "data": serializer.data,
                "message": "OTP retrieved successfully"
            },
            status=status.HTTP_200_OK,
        )
