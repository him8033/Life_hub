from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from account.models import SocialAccount

from account.serializers.socialaccount_crud import (
    SocialAccountListSerializer,
    SocialAccountDetailSerializer,
    SocialAccountCreateSerializer,
    SocialAccountEditSerializer,
    SocialAccountDeleteSerializer,
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
# SOCIAL ACCOUNT CREATE (ADMIN)
# ============================================================


class SocialAccountCreateView(APIView):
    """
    Admin API for creating social accounts manually.
    """

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # ----------------------------------------------------
        # Permission
        # ----------------------------------------------------

        permission_error = check_permission(
            request.user,
            "socialaccount.create",
        )

        if permission_error:
            return permission_error

        # ----------------------------------------------------
        # Validate and create social account
        # ----------------------------------------------------

        serializer = SocialAccountCreateSerializer(
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
        # Get user and provider
        # ----------------------------------------------------

        from account.models import User, SocialProvider

        user = get_object_or_404(User, user_id=serializer.validated_data['user_id'])
        provider = get_object_or_404(SocialProvider, slug=serializer.validated_data['provider_slug'])

        # ----------------------------------------------------
        # Check for duplicate
        # ----------------------------------------------------

        if SocialAccount.objects.filter(
            provider=provider,
            provider_user_id=serializer.validated_data['provider_user_id']
        ).exists():
            return Response(
                {
                    "non_field_errors": [
                        "A social account with this provider and user ID already exists."
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ----------------------------------------------------
        # Create social account
        # ----------------------------------------------------

        socialaccount = SocialAccount.objects.create(
            user=user,
            provider=provider,
            provider_user_id=serializer.validated_data['provider_user_id'],
            provider_email=serializer.validated_data.get('provider_email'),
            provider_username=serializer.validated_data.get('provider_username'),
            avatar_url=serializer.validated_data.get('avatar_url'),
            provider_metadata=serializer.validated_data.get('provider_metadata'),
        )

        return Response(
            {
                "message": "Social account created successfully",
                "data": SocialAccountDetailSerializer(socialaccount).data
            },
            status=status.HTTP_201_CREATED,
        )


# ============================================================
# SOCIAL ACCOUNT LIST
# ============================================================


class SocialAccountListView(APIView):
    """
    Admin API for listing social accounts.

    Supports:
    - Search by user email, provider, provider user ID
    - Filter by provider
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
            "socialaccount.list",
        )

        if permission_error:
            return permission_error

        # ----------------------------------------------------
        # Base queryset
        # ----------------------------------------------------

        socialaccounts = SocialAccount.objects.select_related('user', 'provider').all()

        # ----------------------------------------------------
        # Search
        # ----------------------------------------------------

        search = request.query_params.get("search", "")
        if search:
            socialaccounts = socialaccounts.filter(
                Q(user__email__icontains=search) |
                Q(provider__name__icontains=search) |
                Q(provider__slug__icontains=search) |
                Q(provider_user_id__icontains=search) |
                Q(provider_email__icontains=search)
            )

        # ----------------------------------------------------
        # Filter by provider
        # ----------------------------------------------------

        provider = request.query_params.get("provider")
        if provider and provider.strip():
            socialaccounts = socialaccounts.filter(provider__slug=provider.strip())

        # ----------------------------------------------------
        # Ordering
        # ----------------------------------------------------

        ordering = request.query_params.get("ordering", "-linked_at")
        socialaccounts = socialaccounts.order_by(ordering)

        # ----------------------------------------------------
        # Pagination
        # ----------------------------------------------------

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(socialaccounts, request)

        if page is not None:
            serializer = SocialAccountListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = SocialAccountListSerializer(socialaccounts, many=True)
        return Response(
            {
                "data": serializer.data,
                "message": "Social accounts retrieved successfully"
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# SOCIAL ACCOUNT DETAIL
# ============================================================


class SocialAccountDetailView(APIView):
    """
    Admin API for retrieving social account details.
    """

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request, socialaccount_id):
        # ----------------------------------------------------
        # Permission
        # ----------------------------------------------------

        permission_error = check_permission(
            request.user,
            "socialaccount.view",
        )

        if permission_error:
            return permission_error

        # ----------------------------------------------------
        # Get social account
        # ----------------------------------------------------

        socialaccount = get_object_or_404(
            SocialAccount.objects.select_related('user', 'provider'),
            socialaccount_id=socialaccount_id
        )

        # ----------------------------------------------------
        # Return response
        # ----------------------------------------------------

        serializer = SocialAccountDetailSerializer(socialaccount)

        return Response(
            {
                "data": serializer.data,
                "message": "Social account retrieved successfully"
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# SOCIAL ACCOUNT EDIT
# ============================================================


class SocialAccountEditView(APIView):
    """
    Admin API for editing a social account.
    """

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def put(self, request, socialaccount_id):
        # ----------------------------------------------------
        # Permission
        # ----------------------------------------------------

        permission_error = check_permission(
            request.user,
            "socialaccount.update",
        )

        if permission_error:
            return permission_error

        # ----------------------------------------------------
        # Get social account
        # ----------------------------------------------------

        socialaccount = get_object_or_404(
            SocialAccount.objects.select_related('user', 'provider'),
            socialaccount_id=socialaccount_id
        )

        # ----------------------------------------------------
        # Validate and update social account
        # ----------------------------------------------------

        serializer = SocialAccountEditSerializer(
            socialaccount,
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
        # Update social account and return response
        # ----------------------------------------------------

        socialaccount = serializer.save()

        return Response(
            {
                "message": "Social account updated successfully",
                "data": SocialAccountDetailSerializer(socialaccount).data
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# SOCIAL ACCOUNT DELETE
# ============================================================


class SocialAccountDeleteView(APIView):
    """
    Admin API for deleting a social account.
    """

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def delete(self, request, socialaccount_id):
        # ----------------------------------------------------
        # Permission
        # ----------------------------------------------------

        permission_error = check_permission(
            request.user,
            "socialaccount.delete",
        )

        if permission_error:
            return permission_error

        # ----------------------------------------------------
        # Get social account
        # ----------------------------------------------------

        socialaccount = get_object_or_404(
            SocialAccount.objects.select_related('user'),
            socialaccount_id=socialaccount_id
        )

        # ----------------------------------------------------
        # Delete social account
        # ----------------------------------------------------

        user_email = socialaccount.user.email
        provider_name = socialaccount.provider.name
        socialaccount.delete()

        return Response(
            {
                "message": f"Social account for {user_email} ({provider_name}) deleted successfully."
            },
            status=status.HTTP_200_OK,
        )
