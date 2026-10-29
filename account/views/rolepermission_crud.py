from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from account.models import RolePermission

from account.serializers.rolepermission_crud import (
    RolePermissionListSerializer,
    RolePermissionDetailSerializer,
    RolePermissionCreateSerializer,
    RolePermissionDeleteSerializer,
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
# ROLE PERMISSION CREATE (ADMIN)
# ============================================================


class RolePermissionCreateView(APIView):
    """
    Admin API for assigning a permission to a role.
    """

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # ----------------------------------------------------
        # Permission
        # ----------------------------------------------------

        permission_error = check_permission(
            request.user,
            "rolepermission.create",
        )

        if permission_error:
            return permission_error

        # ----------------------------------------------------
        # Validate and create role permission
        # ----------------------------------------------------

        serializer = RolePermissionCreateSerializer(
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
        # Get role and permission
        # ----------------------------------------------------

        from account.models import Role, Permission

        role = get_object_or_404(Role, slug=serializer.validated_data['role_slug'])
        permission = get_object_or_404(Permission, slug=serializer.validated_data['permission_slug'])

        # ----------------------------------------------------
        # Create role permission
        # ----------------------------------------------------

        rolepermission = RolePermission.objects.create(
            role=role,
            permission=permission,
        )

        return Response(
            {
                "message": "Permission assigned to role successfully",
                "data": RolePermissionDetailSerializer(rolepermission).data
            },
            status=status.HTTP_201_CREATED,
        )


# ============================================================
# ROLE PERMISSION LIST
# ============================================================


class RolePermissionListView(APIView):
    """
    Admin API for listing role permissions.

    Supports:
    - Search by role or permission
    - Filter by role, permission, module
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
            "rolepermission.list",
        )

        if permission_error:
            return permission_error

        # ----------------------------------------------------
        # Base queryset
        # ----------------------------------------------------

        rolepermissions = RolePermission.objects.select_related('role', 'permission').all()

        # ----------------------------------------------------
        # Search
        # ----------------------------------------------------

        search = request.query_params.get("search", "")
        if search:
            rolepermissions = rolepermissions.filter(
                Q(role__name__icontains=search) |
                Q(role__slug__icontains=search) |
                Q(permission__name__icontains=search) |
                Q(permission__slug__icontains=search) |
                Q(permission__module__icontains=search)
            )

        # ----------------------------------------------------
        # Filter by role
        # ----------------------------------------------------

        role = request.query_params.get("role")
        if role and role.strip():
            rolepermissions = rolepermissions.filter(role__slug=role.strip())

        # ----------------------------------------------------
        # Filter by permission
        # ----------------------------------------------------

        permission = request.query_params.get("permission")
        if permission and permission.strip():
            rolepermissions = rolepermissions.filter(permission__slug=permission.strip())

        # ----------------------------------------------------
        # Filter by module
        # ----------------------------------------------------

        module = request.query_params.get("module")
        if module and module.strip():
            rolepermissions = rolepermissions.filter(permission__module=module.strip())

        # ----------------------------------------------------
        # Ordering
        # ----------------------------------------------------

        ordering = request.query_params.get("ordering", "role__name,permission__name")
        if ordering:
            # Split ordering string by comma and apply each order
            order_fields = [field.strip() for field in ordering.split(',') if field.strip()]
            if order_fields:
                rolepermissions = rolepermissions.order_by(*order_fields)
        else:
            rolepermissions = rolepermissions.order_by('role__name', 'permission__name')

        # ----------------------------------------------------
        # Pagination
        # ----------------------------------------------------

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(rolepermissions, request)

        if page is not None:
            serializer = RolePermissionListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = RolePermissionListSerializer(rolepermissions, many=True)
        return Response(
            {
                "data": serializer.data,
                "message": "Role permissions retrieved successfully"
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# ROLE PERMISSION DETAIL
# ============================================================


class RolePermissionDetailView(APIView):
    """
    Admin API for retrieving role permission details.
    """

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request, rolepermission_id):
        # ----------------------------------------------------
        # Permission
        # ----------------------------------------------------

        permission_error = check_permission(
            request.user,
            "rolepermission.view",
        )

        if permission_error:
            return permission_error

        # ----------------------------------------------------
        # Get role permission
        # ----------------------------------------------------

        rolepermission = get_object_or_404(
            RolePermission.objects.select_related('role', 'permission'),
            rolepermission_id=rolepermission_id
        )

        # ----------------------------------------------------
        # Return response
        # ----------------------------------------------------

        serializer = RolePermissionDetailSerializer(rolepermission)

        return Response(
            {
                "data": serializer.data,
                "message": "Role permission retrieved successfully"
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# ROLE PERMISSION DELETE
# ============================================================


class RolePermissionDeleteView(APIView):
    """
    Admin API for removing a permission from a role.
    """

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def delete(self, request, rolepermission_id):
        # ----------------------------------------------------
        # Permission
        # ----------------------------------------------------

        permission_error = check_permission(
            request.user,
            "rolepermission.delete",
        )

        if permission_error:
            return permission_error

        # ----------------------------------------------------
        # Get role permission
        # ----------------------------------------------------

        rolepermission = get_object_or_404(
            RolePermission.objects.select_related('role', 'permission'),
            rolepermission_id=rolepermission_id
        )

        # ----------------------------------------------------
        # Delete role permission
        # ----------------------------------------------------

        role_name = rolepermission.role.name
        permission_name = rolepermission.permission.name
        rolepermission.delete()

        return Response(
            {
                "message": f"Permission '{permission_name}' removed from role '{role_name}' successfully."
            },
            status=status.HTTP_200_OK,
        )
