from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from account.models import LoginHistory

from account.serializers.loginhistory_crud import (
    LoginHistoryListSerializer,
    LoginHistoryDetailSerializer,
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
# LOGIN HISTORY LIST
# ============================================================


class LoginHistoryListView(APIView):
    """
    Admin API for listing login history.

    Supports:
    - Search by user email, login method, IP address
    - Filter by success status, login method
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
            "loginhistory.list",
        )

        if permission_error:
            return permission_error

        # ----------------------------------------------------
        # Base queryset
        # ----------------------------------------------------

        loginhistory = LoginHistory.objects.select_related('user').all()

        # ----------------------------------------------------
        # Search
        # ----------------------------------------------------

        search = request.query_params.get("search", "")
        if search:
            loginhistory = loginhistory.filter(
                Q(user__email__icontains=search) |
                Q(login_method__icontains=search) |
                Q(ip_address__icontains=search) |
                Q(device__icontains=search) |
                Q(browser__icontains=search)
            )

        # ----------------------------------------------------
        # Filter by success status
        # ----------------------------------------------------

        success = request.query_params.get("success")
        if success and success.strip():
            loginhistory = loginhistory.filter(success=success.lower() == "true")

        # ----------------------------------------------------
        # Filter by login method
        # ----------------------------------------------------

        login_method = request.query_params.get("login_method")
        if login_method and login_method.strip():
            loginhistory = loginhistory.filter(login_method=login_method.strip())

        # ----------------------------------------------------
        # Ordering
        # ----------------------------------------------------

        ordering = request.query_params.get("ordering", "-created_at")
        loginhistory = loginhistory.order_by(ordering)

        # ----------------------------------------------------
        # Pagination
        # ----------------------------------------------------

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(loginhistory, request)

        if page is not None:
            serializer = LoginHistoryListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = LoginHistoryListSerializer(loginhistory, many=True)
        return Response(
            {
                "data": serializer.data,
                "message": "Login history retrieved successfully"
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# LOGIN HISTORY DETAIL
# ============================================================


class LoginHistoryDetailView(APIView):
    """
    Admin API for retrieving login history details.
    """

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request, loginhistory_id):
        # ----------------------------------------------------
        # Permission
        # ----------------------------------------------------

        permission_error = check_permission(
            request.user,
            "loginhistory.view",
        )

        if permission_error:
            return permission_error

        # ----------------------------------------------------
        # Get login history
        # ----------------------------------------------------

        loginhistory = get_object_or_404(
            LoginHistory.objects.select_related('user'),
            loginhistory_id=loginhistory_id
        )

        # ----------------------------------------------------
        # Return response
        # ----------------------------------------------------

        serializer = LoginHistoryDetailSerializer(loginhistory)

        return Response(
            {
                "data": serializer.data,
                "message": "Login history retrieved successfully"
            },
            status=status.HTTP_200_OK,
        )
