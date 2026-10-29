from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from account.models import (
    UserStatus,
    User,
)

from account.serializers.status_crud import (
    StatusCreateSerializer,
    StatusEditSerializer,
    StatusListSerializer,
    StatusDetailSerializer,
)

from account.renderers import UserRenderer
from account.pagination import UserAdminPagination

from account.services.permission_service import PermissionService


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
        status.list
        status.view
        status.create
        status.update
        status.delete

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
# STATUS CREATE (ADMIN)
# ============================================================


class StatusCreateView(APIView):
    """
    Admin API for creating new user statuses.
    """

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # ----------------------------------------------------
        # Permission
        # ----------------------------------------------------

        permission_error = check_permission(
            request.user,
            "status.create",
        )

        if permission_error:
            return permission_error

        # ----------------------------------------------------
        # Validate and create status
        # ----------------------------------------------------

        serializer = StatusCreateSerializer(
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
        # Create status and return response
        # ----------------------------------------------------

        user_status = serializer.save()

        return Response(
            {
                "message": "Status created successfully",
                "data": StatusDetailSerializer(user_status).data
            },
            status=status.HTTP_201_CREATED,
        )


# ============================================================
# STATUS LIST
# ============================================================


class StatusListView(APIView):
    """
    Admin API for listing user statuses.

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
            "status.list",
        )

        if permission_error:
            return permission_error

        # ----------------------------------------------------
        # Base queryset
        # ----------------------------------------------------

        statuses = UserStatus.objects.all()

        # ----------------------------------------------------
        # Search
        # ----------------------------------------------------

        search = request.query_params.get("search", "")
        if search:
            statuses = statuses.filter(
                Q(name__icontains=search) |
                Q(slug__icontains=search) |
                Q(description__icontains=search)
            )

        # ----------------------------------------------------
        # Filter by active status
        # ----------------------------------------------------

        is_active = request.query_params.get("is_active")
        if is_active and is_active.strip():
            statuses = statuses.filter(is_active=is_active.lower() == "true")

        # ----------------------------------------------------
        # Ordering
        # ----------------------------------------------------

        ordering = request.query_params.get("ordering", "-created_at")
        statuses = statuses.order_by(ordering)

        # ----------------------------------------------------
        # Pagination
        # ----------------------------------------------------

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(statuses, request)

        if page is not None:
            serializer = StatusListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = StatusListSerializer(statuses, many=True)
        return Response(
            {
                "data": serializer.data,
                "message": "Statuses retrieved successfully"
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# STATUS DETAIL
# ============================================================


class StatusDetailView(APIView):
    """
    Admin API for retrieving user status details.
    """

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request, userstatus_id):
        # ----------------------------------------------------
        # Permission
        # ----------------------------------------------------

        permission_error = check_permission(
            request.user,
            "status.view",
        )

        if permission_error:
            return permission_error

        # ----------------------------------------------------
        # Get status
        # ----------------------------------------------------

        user_status = get_object_or_404(UserStatus, userstatus_id=userstatus_id)

        # ----------------------------------------------------
        # Return response
        # ----------------------------------------------------

        serializer = StatusDetailSerializer(user_status)

        return Response(
            {
                "data": serializer.data,
                "message": "Status retrieved successfully"
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# STATUS EDIT
# ============================================================


class StatusEditView(APIView):
    """
    Admin API for updating a user status.
    """

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def put(self, request, userstatus_id):
        # ----------------------------------------------------
        # Permission
        # ----------------------------------------------------

        permission_error = check_permission(
            request.user,
            "status.update",
        )

        if permission_error:
            return permission_error

        # ----------------------------------------------------
        # Get status
        # ----------------------------------------------------

        user_status = get_object_or_404(UserStatus, userstatus_id=userstatus_id)

        # ----------------------------------------------------
        # Validate and update status
        # ----------------------------------------------------

        serializer = StatusEditSerializer(
            user_status,
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
        # Update status and return response
        # ----------------------------------------------------

        user_status = serializer.save()

        return Response(
            {
                "message": "Status updated successfully",
                "data": StatusDetailSerializer(user_status).data
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# STATUS DELETE
# ============================================================


class StatusDeleteView(APIView):
    """
    Admin API for deleting a user status.
    Performs permanent delete with usage check.
    """

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def delete(self, request, userstatus_id):
        # ----------------------------------------------------
        # Permission
        # ----------------------------------------------------

        permission_error = check_permission(
            request.user,
            "status.delete",
        )

        if permission_error:
            return permission_error

        # ----------------------------------------------------
        # Get status
        # ----------------------------------------------------

        user_status = get_object_or_404(UserStatus, userstatus_id=userstatus_id)

        # ----------------------------------------------------
        # Check if status is in use
        # ----------------------------------------------------

        user_count = User.objects.filter(status=user_status).count()
        if user_count > 0:
            return Response(
                {
                    "non_field_errors": [
                        f"Cannot delete status. It is currently assigned to {user_count} user(s)."
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ----------------------------------------------------
        # Delete status
        # ----------------------------------------------------

        user_status.delete()

        return Response(
            {
                "message": "Status deleted successfully."
            },
            status=status.HTTP_200_OK,
        )
