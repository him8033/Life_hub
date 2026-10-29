from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from account.models import (
    Role,
    UserRole,
    RolePermission,
)

from account.serializers.role_crud import (
    RoleCreateSerializer,
    RoleEditSerializer,
    RoleListSerializer,
    RoleDetailSerializer,
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
        role.list
        role.view
        role.create
        role.update
        role.delete

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
# ROLE CREATE (ADMIN)
# ============================================================


class RoleCreateView(APIView):
    """
    Admin API for creating new roles.
    """

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # ----------------------------------------------------
        # Permission
        # ----------------------------------------------------

        permission_error = check_permission(
            request.user,
            "role.create",
        )

        if permission_error:
            return permission_error

        # ----------------------------------------------------
        # Validate and create role
        # ----------------------------------------------------

        serializer = RoleCreateSerializer(
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
        # Create role and return response
        # ----------------------------------------------------

        role = serializer.save()

        return Response(
            {
                "message": "Role created successfully",
                "data": RoleDetailSerializer(role).data
            },
            status=status.HTTP_201_CREATED,
        )


# ============================================================
# ROLE LIST
# ============================================================


class RoleListView(APIView):
    """
    Admin API for listing roles.

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
            "role.list",
        )

        if permission_error:
            return permission_error

        # ----------------------------------------------------
        # Base queryset
        # ----------------------------------------------------

        roles = Role.objects.all()

        # ----------------------------------------------------
        # Search
        # ----------------------------------------------------

        search = request.query_params.get("search", "")
        if search:
            roles = roles.filter(
                Q(name__icontains=search) |
                Q(slug__icontains=search) |
                Q(description__icontains=search)
            )

        # ----------------------------------------------------
        # Filter by active status
        # ----------------------------------------------------

        is_active = request.query_params.get("is_active")
        if is_active and is_active.strip():
            roles = roles.filter(is_active=is_active.lower() == "true")

        # ----------------------------------------------------
        # Ordering
        # ----------------------------------------------------

        ordering = request.query_params.get("ordering", "-created_at")
        roles = roles.order_by(ordering)

        # ----------------------------------------------------
        # Pagination
        # ----------------------------------------------------

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(roles, request)

        if page is not None:
            serializer = RoleListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = RoleListSerializer(roles, many=True)
        return Response(
            {
                "data": serializer.data,
                "message": "Roles retrieved successfully"
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# ROLE DETAIL
# ============================================================


class RoleDetailView(APIView):
    """
    Admin API for retrieving role details.
    """

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request, role_id):
        # ----------------------------------------------------
        # Permission
        # ----------------------------------------------------

        permission_error = check_permission(
            request.user,
            "role.view",
        )

        if permission_error:
            return permission_error

        # ----------------------------------------------------
        # Get role
        # ----------------------------------------------------

        role = get_object_or_404(Role, role_id=role_id)

        # ----------------------------------------------------
        # Return response
        # ----------------------------------------------------

        serializer = RoleDetailSerializer(role)

        return Response(
            {
                "data": serializer.data,
                "message": "Role retrieved successfully"
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# ROLE EDIT
# ============================================================


class RoleEditView(APIView):
    """
    Admin API for updating a role.
    """

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def put(self, request, role_id):
        # ----------------------------------------------------
        # Permission
        # ----------------------------------------------------

        permission_error = check_permission(
            request.user,
            "role.update",
        )

        if permission_error:
            return permission_error

        # ----------------------------------------------------
        # Get role
        # ----------------------------------------------------

        role = get_object_or_404(Role, role_id=role_id)

        # ----------------------------------------------------
        # Validate and update role
        # ----------------------------------------------------

        serializer = RoleEditSerializer(
            role,
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
        # Update role and return response
        # ----------------------------------------------------

        role = serializer.save()

        return Response(
            {
                "message": "Role updated successfully",
                "data": RoleDetailSerializer(role).data
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# ROLE DELETE
# ============================================================


class RoleDeleteView(APIView):
    """
    Admin API for deleting a role.
    Performs permanent delete with usage check.
    """

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def delete(self, request, role_id):
        # ----------------------------------------------------
        # Permission
        # ----------------------------------------------------

        permission_error = check_permission(
            request.user,
            "role.delete",
        )

        if permission_error:
            return permission_error

        # ----------------------------------------------------
        # Get role
        # ----------------------------------------------------

        role = get_object_or_404(Role, role_id=role_id)

        # ----------------------------------------------------
        # Check if role is in use
        # ----------------------------------------------------

        user_count = UserRole.objects.filter(role=role).count()
        if user_count > 0:
            return Response(
                {
                    "non_field_errors": [
                        f"Cannot delete role. It is currently assigned to {user_count} user(s)."
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ----------------------------------------------------
        # Delete role
        # ----------------------------------------------------

        role.delete()

        return Response(
            {
                "message": "Role deleted successfully."
            },
            status=status.HTTP_200_OK,
        )
