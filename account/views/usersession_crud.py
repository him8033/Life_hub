from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from account.models import UserSession

from account.serializers.usersession_crud import (
    UserSessionListSerializer,
    UserSessionDetailSerializer,
    UserSessionRevokeSerializer,
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
# USER SESSION LIST
# ============================================================


class UserSessionListView(APIView):
    """
    Admin API for listing user sessions.

    Supports:
    - Search by user email, device, browser, IP address
    - Filter by active status
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
            "usersession.list",
        )

        if permission_error:
            return permission_error

        # ----------------------------------------------------
        # Base queryset
        # ----------------------------------------------------

        sessions = UserSession.objects.select_related('user').all()

        # ----------------------------------------------------
        # Search
        # ----------------------------------------------------

        search = request.query_params.get("search", "")
        if search:
            sessions = sessions.filter(
                Q(user__email__icontains=search) |
                Q(device__icontains=search) |
                Q(browser__icontains=search) |
                Q(ip_address__icontains=search)
            )

        # ----------------------------------------------------
        # Filter by active status
        # ----------------------------------------------------

        is_active = request.query_params.get("is_active")
        if is_active and is_active.strip():
            sessions = sessions.filter(is_active=is_active.lower() == "true")

        # ----------------------------------------------------
        # Ordering
        # ----------------------------------------------------

        ordering = request.query_params.get("ordering", "-created_at")
        sessions = sessions.order_by(ordering)

        # ----------------------------------------------------
        # Pagination
        # ----------------------------------------------------

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(sessions, request)

        if page is not None:
            serializer = UserSessionListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = UserSessionListSerializer(sessions, many=True)
        return Response(
            {
                "data": serializer.data,
                "message": "User sessions retrieved successfully"
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# USER SESSION DETAIL
# ============================================================


class UserSessionDetailView(APIView):
    """
    Admin API for retrieving user session details.
    """

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request, usersession_id):
        # ----------------------------------------------------
        # Permission
        # ----------------------------------------------------

        permission_error = check_permission(
            request.user,
            "usersession.view",
        )

        if permission_error:
            return permission_error

        # ----------------------------------------------------
        # Get user session
        # ----------------------------------------------------

        session = get_object_or_404(
            UserSession.objects.select_related('user'),
            usersession_id=usersession_id
        )

        # ----------------------------------------------------
        # Return response
        # ----------------------------------------------------

        serializer = UserSessionDetailSerializer(session)

        return Response(
            {
                "data": serializer.data,
                "message": "User session retrieved successfully"
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# USER SESSION REVOKE
# ============================================================


class UserSessionRevokeView(APIView):
    """
    Admin API for revoking a user session.
    """

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request, usersession_id):
        # ----------------------------------------------------
        # Permission
        # ----------------------------------------------------

        permission_error = check_permission(
            request.user,
            "usersession.revoke",
        )

        if permission_error:
            return permission_error

        # ----------------------------------------------------
        # Get user session
        # ----------------------------------------------------

        session = get_object_or_404(
            UserSession.objects.select_related('user'),
            usersession_id=usersession_id
        )

        # ----------------------------------------------------
        # Validate and revoke session
        # ----------------------------------------------------

        serializer = UserSessionRevokeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        reason = serializer.validated_data.get('reason', 'Revoked by admin')

        # ----------------------------------------------------
        # Revoke session
        # ----------------------------------------------------

        session.revoke(reason=reason)

        return Response(
            {
                "message": f"Session for {session.user.email} revoked successfully."
            },
            status=status.HTTP_200_OK,
        )
