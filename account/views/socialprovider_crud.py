from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from account.models import SocialProvider

from account.serializers.socialprovider_crud import (
    SocialProviderCreateSerializer,
    SocialProviderEditSerializer,
    SocialProviderListSerializer,
    SocialProviderDetailSerializer,
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
        socialprovider.list
        socialprovider.view
        socialprovider.create
        socialprovider.update
        socialprovider.delete

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
# SOCIAL PROVIDER CREATE (ADMIN)
# ============================================================


class SocialProviderCreateView(APIView):
    """
    Admin API for creating new social providers.
    """

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # ----------------------------------------------------
        # Permission
        # ----------------------------------------------------

        permission_error = check_permission(
            request.user,
            "socialprovider.create",
        )

        if permission_error:
            return permission_error

        # ----------------------------------------------------
        # Validate and create social provider
        # ----------------------------------------------------

        serializer = SocialProviderCreateSerializer(
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
        # Create social provider and return response
        # ----------------------------------------------------

        socialprovider = serializer.save()

        return Response(
            {
                "message": "Social provider created successfully",
                "data": SocialProviderDetailSerializer(socialprovider).data
            },
            status=status.HTTP_201_CREATED,
        )


# ============================================================
# SOCIAL PROVIDER LIST
# ============================================================


class SocialProviderListView(APIView):
    """
    Admin API for listing social providers.

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
            "socialprovider.list",
        )

        if permission_error:
            return permission_error

        # ----------------------------------------------------
        # Base queryset
        # ----------------------------------------------------

        socialproviders = SocialProvider.objects.all()

        # ----------------------------------------------------
        # Search
        # ----------------------------------------------------

        search = request.query_params.get("search", "")
        if search:
            socialproviders = socialproviders.filter(
                Q(name__icontains=search) |
                Q(slug__icontains=search) |
                Q(description__icontains=search)
            )

        # ----------------------------------------------------
        # Filter by active status
        # ----------------------------------------------------

        is_active = request.query_params.get("is_active")
        if is_active and is_active.strip():
            socialproviders = socialproviders.filter(is_active=is_active.lower() == "true")

        # ----------------------------------------------------
        # Ordering
        # ----------------------------------------------------

        ordering = request.query_params.get("ordering", "name")
        socialproviders = socialproviders.order_by(ordering)

        # ----------------------------------------------------
        # Pagination
        # ----------------------------------------------------

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(socialproviders, request)

        if page is not None:
            serializer = SocialProviderListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = SocialProviderListSerializer(socialproviders, many=True)
        return Response(
            {
                "data": serializer.data,
                "message": "Social providers retrieved successfully"
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# SOCIAL PROVIDER DETAIL
# ============================================================


class SocialProviderDetailView(APIView):
    """
    Admin API for retrieving social provider details.
    """

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request, socialprovider_id):
        # ----------------------------------------------------
        # Permission
        # ----------------------------------------------------

        permission_error = check_permission(
            request.user,
            "socialprovider.view",
        )

        if permission_error:
            return permission_error

        # ----------------------------------------------------
        # Get social provider
        # ----------------------------------------------------

        socialprovider = get_object_or_404(SocialProvider, socialprovider_id=socialprovider_id)

        # ----------------------------------------------------
        # Return response
        # ----------------------------------------------------

        serializer = SocialProviderDetailSerializer(socialprovider)

        return Response(
            {
                "data": serializer.data,
                "message": "Social provider retrieved successfully"
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# SOCIAL PROVIDER EDIT
# ============================================================


class SocialProviderEditView(APIView):
    """
    Admin API for updating a social provider.
    """

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def put(self, request, socialprovider_id):
        # ----------------------------------------------------
        # Permission
        # ----------------------------------------------------

        permission_error = check_permission(
            request.user,
            "socialprovider.update",
        )

        if permission_error:
            return permission_error

        # ----------------------------------------------------
        # Get social provider
        # ----------------------------------------------------

        socialprovider = get_object_or_404(SocialProvider, socialprovider_id=socialprovider_id)

        # ----------------------------------------------------
        # Validate and update social provider
        # ----------------------------------------------------

        serializer = SocialProviderEditSerializer(
            socialprovider,
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
        # Update social provider and return response
        # ----------------------------------------------------

        socialprovider = serializer.save()

        return Response(
            {
                "message": "Social provider updated successfully",
                "data": SocialProviderDetailSerializer(socialprovider).data
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# SOCIAL PROVIDER DELETE
# ============================================================


class SocialProviderDeleteView(APIView):
    """
    Admin API for deleting a social provider.
    Performs permanent delete with usage check.
    """

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def delete(self, request, socialprovider_id):
        # ----------------------------------------------------
        # Permission
        # ----------------------------------------------------

        permission_error = check_permission(
            request.user,
            "socialprovider.delete",
        )

        if permission_error:
            return permission_error

        # ----------------------------------------------------
        # Get social provider
        # ----------------------------------------------------

        socialprovider = get_object_or_404(SocialProvider, socialprovider_id=socialprovider_id)

        # ----------------------------------------------------
        # Check if social provider is in use
        # ----------------------------------------------------

        from account.models import SocialAccount

        socialaccount_count = SocialAccount.objects.filter(provider=socialprovider).count()
        if socialaccount_count > 0:
            return Response(
                {
                    "non_field_errors": [
                        f"Cannot delete social provider. It is currently used in {socialaccount_count} social account(s)."
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ----------------------------------------------------
        # Delete social provider
        # ----------------------------------------------------

        socialprovider.delete()

        return Response(
            {
                "message": "Social provider deleted successfully."
            },
            status=status.HTTP_200_OK,
        )
