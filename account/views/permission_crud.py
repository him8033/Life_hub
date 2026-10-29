from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from account.models import Permission

from account.serializers.permission_crud import (
    PermissionCreateSerializer,
    PermissionEditSerializer,
    PermissionListSerializer,
    PermissionDetailSerializer,
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
        permission.list
        permission.view
        permission.create
        permission.update
        permission.delete

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
# PERMISSION CREATE (ADMIN)
# ============================================================


class PermissionCreateView(APIView):
    """
    Admin API for creating new permissions.
    """

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # ----------------------------------------------------
        # Permission
        # ----------------------------------------------------

        permission_error = check_permission(
            request.user,
            "permission.create",
        )

        if permission_error:
            return permission_error

        # ----------------------------------------------------
        # Validate and create permission
        # ----------------------------------------------------

        serializer = PermissionCreateSerializer(
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
        # Create permission and return response
        # ----------------------------------------------------

        permission = serializer.save()

        return Response(
            {
                "message": "Permission created successfully",
                "data": PermissionDetailSerializer(permission).data
            },
            status=status.HTTP_201_CREATED,
        )


# ============================================================
# PERMISSION LIST
# ============================================================


class PermissionListView(APIView):
    """
    Admin API for listing permissions.

    Supports:
    - Search
    - Active status filter
    - Module filter
    - Ordering
    - Pagination
    """

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    pagination_class = UserAdminPagination


class PermissionListView(APIView):
    """
    Admin API for listing permissions.

    Supports:
    - Search
    - Active status filter
    - Module filter
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
            "permission.list",
        )

        if permission_error:
            return permission_error

        # ----------------------------------------------------
        # Base queryset
        # ----------------------------------------------------

        permissions = Permission.objects.all()

        # ----------------------------------------------------
        # Search
        # ----------------------------------------------------

        search = request.query_params.get(
            "search",
            "",
        ).strip()

        if search:
            permissions = permissions.filter(
                Q(name__icontains=search)
                | Q(slug__icontains=search)
                | Q(description__icontains=search)
            )

        # ----------------------------------------------------
        # Filter by active status
        # ----------------------------------------------------

        is_active = request.query_params.get(
            "is_active",
        )

        if is_active and is_active.strip():
            permissions = permissions.filter(
                is_active=is_active.lower() == "true"
            )

        # ----------------------------------------------------
        # Filter by module
        # ----------------------------------------------------

        module = request.query_params.get(
            "module",
            "",
        ).strip()

        if module:
            permissions = permissions.filter(
                module=module
            )

        # ----------------------------------------------------
        # Ordering
        # ----------------------------------------------------

        ordering = request.query_params.get(
            "ordering",
            "module,name",
        )

        allowed_ordering = {
            "module",
            "-module",
            "name",
            "-name",
            "slug",
            "-slug",
            "created_at",
            "-created_at",
            "updated_at",
            "-updated_at",
        }

        ordering_fields = [
            field.strip()
            for field in ordering.split(",")
            if field.strip()
        ]

        valid_ordering = [
            field
            for field in ordering_fields
            if field in allowed_ordering
        ]

        if valid_ordering:
            permissions = permissions.order_by(
                *valid_ordering
            )
        else:
            permissions = permissions.order_by(
                "module",
                "name",
            )

        # ----------------------------------------------------
        # Pagination
        # ----------------------------------------------------

        paginator = self.pagination_class()

        page = paginator.paginate_queryset(
            permissions,
            request,
            view=self,
        )

        if page is not None:
            serializer = PermissionListSerializer(
                page,
                many=True,
            )

            return paginator.get_paginated_response(
                serializer.data
            )

        # ----------------------------------------------------
        # Non-paginated fallback
        # ----------------------------------------------------

        serializer = PermissionListSerializer(
            permissions,
            many=True,
        )

        return Response(
            {
                "data": serializer.data,
                "message": "Permissions retrieved successfully",
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# PERMISSION DETAIL
# ============================================================


class PermissionDetailView(APIView):
    """
    Admin API for retrieving permission details.
    """

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request, permission_id):
        # ----------------------------------------------------
        # Permission
        # ----------------------------------------------------

        permission_error = check_permission(
            request.user,
            "permission.view",
        )

        if permission_error:
            return permission_error

        # ----------------------------------------------------
        # Get permission
        # ----------------------------------------------------

        permission = get_object_or_404(Permission, permission_id=permission_id)

        # ----------------------------------------------------
        # Return response
        # ----------------------------------------------------

        serializer = PermissionDetailSerializer(permission)

        return Response(
            {
                "data": serializer.data,
                "message": "Permission retrieved successfully"
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# PERMISSION EDIT
# ============================================================


class PermissionEditView(APIView):
    """
    Admin API for updating a permission.
    """

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def put(self, request, permission_id):
        # ----------------------------------------------------
        # Permission
        # ----------------------------------------------------

        permission_error = check_permission(
            request.user,
            "permission.update",
        )

        if permission_error:
            return permission_error

        # ----------------------------------------------------
        # Get permission
        # ----------------------------------------------------

        permission = get_object_or_404(Permission, permission_id=permission_id)

        # ----------------------------------------------------
        # Validate and update permission
        # ----------------------------------------------------

        serializer = PermissionEditSerializer(
            permission,
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
        # Update permission and return response
        # ----------------------------------------------------

        permission = serializer.save()

        return Response(
            {
                "message": "Permission updated successfully",
                "data": PermissionDetailSerializer(permission).data
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# PERMISSION DELETE
# ============================================================


class PermissionDeleteView(APIView):
    """
    Admin API for deleting a permission.
    Performs permanent delete with usage check.
    """

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def delete(self, request, permission_id):
        # ----------------------------------------------------
        # Permission
        # ----------------------------------------------------

        permission_error = check_permission(
            request.user,
            "permission.delete",
        )

        if permission_error:
            return permission_error

        # ----------------------------------------------------
        # Get permission
        # ----------------------------------------------------

        permission = get_object_or_404(Permission, permission_id=permission_id)

        # ----------------------------------------------------
        # Check if permission is in use
        # ----------------------------------------------------

        from account.models import RolePermission

        rolepermission_count = RolePermission.objects.filter(
            permission=permission).count()
        if rolepermission_count > 0:
            return Response(
                {
                    "non_field_errors": [
                        f"Cannot delete permission. It is currently assigned to {rolepermission_count} role(s)."
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ----------------------------------------------------
        # Delete permission
        # ----------------------------------------------------

        permission.delete()

        return Response(
            {
                "message": "Permission deleted successfully."
            },
            status=status.HTTP_200_OK,
        )
