from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from account.models import (
    User,
    Role,
    UserRole,
    UserStatus,
)

from account.serializers.user import (
    UserProfileSerializer,
)

from account.serializers.user_crud import (
    UserEditSerializer,
    UserStatusUpdateSerializer,
    UserDeleteSerializer,
    AdminUserCreateSerializer,
)

from account.renderers import UserRenderer
from account.pagination import UserAdminPagination

from account.services.auth_service import AuthService
from account.services.session_service import SessionService
from account.services.email_service import EmailService
from account.services.permission_service import PermissionService
from account.services.status_service import StatusService


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
        user.list
        user.view
        role.manage
        status.manage
        user.block
        user.delete
        user.change_password

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
        PermissionService.user_has_permission(
            user,
            permission_slug,
        )
    )

    if not has_permission:
        synonyms = {
            "user.list": ["user.read"],
            "user.view": ["user.read"],
            "user.edit": ["user.update"],
            "user.read": ["user.list", "user.view"],
            "user.update": ["user.edit"],
        }
        for alt in synonyms.get(permission_slug, []):
            if PermissionService.user_has_permission(user, alt):
                has_permission = True
                break

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
# USER CREATE (ADMIN)
# ============================================================


class UserCreateView(APIView):
    """
    Admin API for creating new users without OTP verification.
    Users are created with pending status by default.
    """

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # ----------------------------------------------------
        # Permission
        # ----------------------------------------------------

        permission_error = check_permission(
            request.user,
            "user.create",
        )

        if permission_error:
            return permission_error

        # ----------------------------------------------------
        # Validate and create user
        # ----------------------------------------------------

        serializer = AdminUserCreateSerializer(
            data=request.data,
            context={
                "admin_user": request.user
            }
        )

        if not serializer.is_valid():
            return Response(
                {
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ----------------------------------------------------
        # Create user and return response
        # ----------------------------------------------------

        result = serializer.save()

        return Response(
            result,
            status=status.HTTP_201_CREATED,
        )


# ============================================================
# USER LIST
# ============================================================


class UserListView(APIView):
    """
    Admin API for listing users.

    Supports:
    - Search
    - Status filter
    - Role filter
    - Ordering
    - Pagination
    """

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request):

        # ----------------------------------------------------
        # Permission
        # ----------------------------------------------------

        permission_error = check_permission(
            request.user,
            "user.list",
        )

        if permission_error:
            return permission_error

        # ----------------------------------------------------
        # Base queryset
        # ----------------------------------------------------

        users = User.objects.filter(
            deleted_at__isnull=True
        )

        # ----------------------------------------------------
        # Search
        # ----------------------------------------------------

        search = request.query_params.get(
            "search"
        )

        if search:

            users = users.filter(
                Q(email__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
            )

        # ----------------------------------------------------
        # Status filter
        # ----------------------------------------------------

        status_slug = request.query_params.get(
            "status"
        )

        if status_slug:

            users = users.filter(
                status__slug=status_slug
            )

        # ----------------------------------------------------
        # Role filter
        # ----------------------------------------------------

        role_slug = request.query_params.get(
            "role"
        )

        if role_slug:

                users = users.filter(
                    user_roles__role__slug=role_slug,
                    user_roles__role__is_active=True,
                ).distinct()

        # ----------------------------------------------------
        # Ordering
        # ----------------------------------------------------

        ordering = request.query_params.get(
            "ordering",
            "-created_at",
        )

        allowed_ordering = [
            "email",
            "-email",
            "first_name",
            "-first_name",
            "last_name",
            "-last_name",
            "created_at",
            "-created_at",
        ]

        if ordering in allowed_ordering:

            users = users.order_by(
                ordering
            )

        else:

            users = users.order_by(
                "-created_at"
            )

        # ----------------------------------------------------
        # Pagination
        # ----------------------------------------------------

        paginator = UserAdminPagination()

        page = paginator.paginate_queryset(
            users,
            request,
            view=self,
        )

        serializer = UserProfileSerializer(
            page,
            many=True,
        )

        return paginator.get_paginated_response(
            serializer.data
        )


# ============================================================
# USER DETAIL
# ============================================================


class UserDetailView(APIView):
    """
    Admin API for viewing a single user.
    """

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(
        self,
        request,
        user_id,
    ):

        # ----------------------------------------------------
        # Permission
        # ----------------------------------------------------

        permission_error = check_permission(
            request.user,
            "user.view",
        )

        if permission_error:
            return permission_error

        # ----------------------------------------------------
        # Get user
        # ----------------------------------------------------

        user = get_object_or_404(
            User,
            user_id=user_id,
            deleted_at__isnull=True,
        )

        # ----------------------------------------------------
        # Serialize
        # ----------------------------------------------------

        serializer = UserProfileSerializer(
            user
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


# ============================================================
# USER EDIT
# ============================================================


class UserEditView(APIView):
    """
    Admin API for editing a user.

    Supports:

    1. Basic profile fields

    {
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "9876543210"
    }

    2. Roles

    {
        "roles": [
            "admin",
            "editor"
        ]
    }

    3. Password

    {
        "new_password": "NewPassword@123",
        "confirm_password": "NewPassword@123"
    }

    4. Combined

    {
        "first_name": "John",
        "roles": [
            "admin"
        ],
        "new_password": "NewPassword@123",
        "confirm_password": "NewPassword@123",
        "send_email": true
    }

    Permissions:

    Profile:
        user.edit

    Roles:
        role.manage

    Password:
        user.change_password
    """

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def put(
        self,
        request,
        user_id,
    ):

        # ----------------------------------------------------
        # Get user
        # ----------------------------------------------------

        user = get_object_or_404(
            User,
            user_id=user_id,
            deleted_at__isnull=True,
        )

        # ----------------------------------------------------
        # Validate request
        # ----------------------------------------------------

        serializer = UserEditSerializer(
            user,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True
        )

        validated_data = serializer.validated_data

        # ----------------------------------------------------
        # Detect requested operations
        # ----------------------------------------------------

        editable_fields = {
            "first_name",
            "last_name",
            "phone_number",
        }

        has_profile_update = any(
            field in validated_data
            for field in editable_fields
        )

        has_role_update = (
            "roles" in validated_data
        )

        has_password_update = (
            "new_password" in validated_data
        )

        # ----------------------------------------------------
        # Make sure something is being updated
        # ----------------------------------------------------

        if not (
            has_profile_update
            or has_role_update
            or has_password_update
        ):
            return Response(
                {
                    "non_field_errors": [
                        "No fields provided for update."
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ----------------------------------------------------
        # Permission checks
        # ----------------------------------------------------

        if has_profile_update:

            permission_error = check_permission(
                request.user,
                "user.edit",
            )

            if permission_error:
                return permission_error

        if has_role_update:

            permission_error = check_permission(
                request.user,
                "role.manage",
            )

            if permission_error:
                return permission_error

        if has_password_update:

            permission_error = check_permission(
                request.user,
                "user.change_password",
            )

            if permission_error:
                return permission_error

        # ----------------------------------------------------
        # Extract special fields
        # ----------------------------------------------------

        roles = validated_data.pop(
            "roles",
            None,
        )

        new_password = validated_data.pop(
            "new_password",
            None,
        )

        validated_data.pop(
            "confirm_password",
            None,
        )

        send_email = validated_data.pop(
            "send_email",
            False,
        )

        # ----------------------------------------------------
        # Store old roles
        # ----------------------------------------------------

        old_roles = []

        if has_role_update:

            old_roles = list(
                UserRole.objects.filter(
                    user=user
                )
                .select_related("role")
                .values_list(
                    "role__slug",
                    flat=True,
                )
            )

        # ====================================================
        # ROLE VALIDATION
        # ====================================================

        role_objects = []
        role_slugs = []

        if has_role_update:

            # ------------------------------------------------
            # Remove duplicate roles
            # ------------------------------------------------

            role_slugs = list(
                dict.fromkeys(
                    roles
                )
            )

            # ------------------------------------------------
            # Get roles
            # ------------------------------------------------

            role_objects = list(
                Role.objects.filter(
                    slug__in=role_slugs,
                    is_active=True,
                )
            )

            # ------------------------------------------------
            # Find invalid roles
            # ------------------------------------------------

            found_slugs = {
                role.slug
                for role in role_objects
            }

            invalid_roles = [
                slug
                for slug in role_slugs
                if slug not in found_slugs
            ]

            if invalid_roles:

                return Response(
                    {
                        "non_field_errors": [
                            (
                                "Invalid role(s): "
                                + ", ".join(
                                    invalid_roles
                                )
                            )
                        ]
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # ====================================================
        # DATABASE TRANSACTION
        # ====================================================

        with transaction.atomic():

            # ------------------------------------------------
            # Profile update
            # ------------------------------------------------

            if has_profile_update:

                for field, value in validated_data.items():

                    setattr(
                        user,
                        field,
                        value,
                    )

                update_fields = [
                    field
                    for field in editable_fields
                    if field in validated_data
                ]

                update_fields.append(
                    "updated_at"
                )

                user.save(
                    update_fields=update_fields
                )

            # ------------------------------------------------
            # Role update
            # ------------------------------------------------

            if has_role_update:

                UserRole.objects.filter(
                    user=user
                ).delete()

                for role in role_objects:
                    UserRole.objects.create(
                        user=user,
                        role=role,
                        assigned_by=request.user,
                    )

            # ------------------------------------------------
            # Password update
            # ------------------------------------------------

            if has_password_update:

                result = AuthService.admin_change_password(
                    user=user,
                    new_password=new_password,
                )

                if not result["success"]:
                    return Response(
                        {
                            "non_field_errors": [
                                result["error"]
                            ]
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # --------------------------------------------
                # Revoke all sessions
                # --------------------------------------------

                SessionService.revoke_all_sessions(
                    user
                )

        # ====================================================
        # EMAIL NOTIFICATION
        # ====================================================

        if send_email:

            changes = []

            # ------------------------------------------------
            # Profile changes
            # ------------------------------------------------

            if has_profile_update:

                changed_fields = []

                if "first_name" in validated_data:
                    changed_fields.append(
                        "First name"
                    )

                if "last_name" in validated_data:
                    changed_fields.append(
                        "Last name"
                    )

                if "phone_number" in validated_data:
                    changed_fields.append(
                        "Phone number"
                    )

                if changed_fields:

                    changes.append(
                        "Profile information updated: "
                        + ", ".join(
                            changed_fields
                        )
                    )

            # ------------------------------------------------
            # Role changes
            # ------------------------------------------------

            if has_role_update:

                old_roles_text = (
                    ", ".join(old_roles)
                    if old_roles
                    else "No roles assigned"
                )

                new_roles_text = (
                    ", ".join(role_slugs)
                    if role_slugs
                    else "No roles assigned"
                )

                changes.append(
                    "Roles changed from "
                    f"({old_roles_text}) "
                    f"to ({new_roles_text})"
                )

            # ------------------------------------------------
            # Password changes
            # ------------------------------------------------

            if has_password_update:

                changes.append(
                    "Password changed"
                )

            # ------------------------------------------------
            # Send ONE email
            # ------------------------------------------------

            EmailService.send_user_edit_email(
                to_email=user.email,
                changes=changes,
                admin_email=request.user.email,
            )

        # ----------------------------------------------------
        # Refresh
        # ----------------------------------------------------

        user.refresh_from_db()

        response_serializer = UserProfileSerializer(
            user
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )


# ============================================================
# USER STATUS / BLOCK / UNBLOCK
# ============================================================


class UserStatusUpdateView(APIView):
    """
    Admin API for updating status or blocking/unblocking.

    Status:

    {
        "status_slug": "active",
        "reason": "Account reviewed and activated",
        "send_email": true
    }

    Block:

    {
        "action": "block",
        "reason": "Policy violation",
        "send_email": true
    }

    Unblock:

    {
        "action": "unblock",
        "reason": "Issue resolved",
        "send_email": true
    }

    Permissions:

    Status:
        status.manage

    Block / Unblock:
        user.block
    """

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def patch(
        self,
        request,
        user_id,
    ):

        # ----------------------------------------------------
        # Get user
        # ----------------------------------------------------

        user = get_object_or_404(
            User,
            user_id=user_id,
            deleted_at__isnull=True,
        )

        # ----------------------------------------------------
        # Validate
        # ----------------------------------------------------

        serializer = UserStatusUpdateSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        validated_data = (
            serializer.validated_data
        )

        status_slug = validated_data.get(
            "status_slug"
        )

        action = validated_data.get(
            "action"
        )

        reason = validated_data.get(
            "reason",
            "",
        )

        send_email = validated_data.get(
            "send_email",
            False,
        )

        # ----------------------------------------------------
        # Store old status BEFORE modification
        # ----------------------------------------------------

        old_status = (
            user.status.slug
            if user.status
            else None
        )

        # ====================================================
        # NORMAL STATUS UPDATE
        # ====================================================

        if status_slug:

            # ------------------------------------------------
            # Permission
            # ------------------------------------------------

            permission_error = check_permission(
                request.user,
                "status.manage",
            )

            if permission_error:
                return permission_error

            # ------------------------------------------------
            # Get status
            # ------------------------------------------------

            user_status = get_object_or_404(
                UserStatus,
                slug=status_slug,
                is_active=True,
            )

            # ------------------------------------------------
            # Update status
            # ------------------------------------------------

            user.status = user_status

            update_fields = [
                "status",
                "updated_at",
            ]

            if status_slug == "active" and not user.email_verified:
                user.email_verified = True
                user.email_verified_at = timezone.now()
                update_fields.extend([
                    "email_verified",
                    "email_verified_at",
                ])

            user.save(
                update_fields=update_fields
            )

            StatusService.clear_user_status_cache(user)

        # ====================================================
        # BLOCK / UNBLOCK
        # ====================================================

        elif action:

            # ------------------------------------------------
            # Permission
            # ------------------------------------------------

            permission_error = check_permission(
                request.user,
                "user.block",
            )

            if permission_error:
                return permission_error

            # ------------------------------------------------
            # Block
            # ------------------------------------------------

            if action == "block":

                AuthService.block_user(
                    user_id=user.user_id,
                    blocked_by=request.user.user_id,
                    reason=reason,
                )

            # ------------------------------------------------
            # Unblock
            # ------------------------------------------------

            elif action == "unblock":

                AuthService.unblock_user(
                    user_id=user.user_id,
                    unblocked_by=request.user.user_id,
                    reason=reason,
                )

        # ----------------------------------------------------
        # Refresh user after status modification
        # ----------------------------------------------------

        user.refresh_from_db()

        # ====================================================
        # ONE STATUS EMAIL
        # ====================================================

        if send_email:

            new_status = (
                user.status.slug
                if user.status
                else None
            )

            EmailService.send_status_change_email(
                to_email=user.email,
                old_status=old_status,
                new_status=new_status,
                reason=reason,
                admin_email=request.user.email,
            )

        # ----------------------------------------------------
        # Serialize response
        # ----------------------------------------------------

        response_serializer = (
            UserProfileSerializer(user)
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )


# ============================================================
# USER DELETE
# ============================================================


class UserDeleteView(APIView):
    """
    Admin API for soft or permanent deletion.

    Soft delete:

    {
        "permanent": false,
        "reason": "Account requested deletion",
        "send_email": true
    }

    Permanent delete:

    {
        "permanent": true,
        "reason": "Administrative deletion"
    }
    """

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def delete(
        self,
        request,
        user_id,
    ):

        # ----------------------------------------------------
        # Permission
        # ----------------------------------------------------

        permission_error = check_permission(
            request.user,
            "user.delete",
        )

        if permission_error:
            return permission_error

        # ----------------------------------------------------
        # Get user
        # ----------------------------------------------------

        user = get_object_or_404(
            User,
            user_id=user_id,
            deleted_at__isnull=True,
        )

        # ----------------------------------------------------
        # Validate
        # ----------------------------------------------------

        serializer = UserDeleteSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        permanent = serializer.validated_data.get(
            "permanent",
            False,
        )

        reason = serializer.validated_data.get(
            "reason",
            "",
        )

        send_email = serializer.validated_data.get(
            "send_email",
            False,
        )

        # ----------------------------------------------------
        # Save email before deletion
        # ----------------------------------------------------

        user_email = user.email

        # ====================================================
        # PERMANENT DELETE
        # ====================================================

        if permanent:

            # ------------------------------------------------
            # Revoke sessions
            # ------------------------------------------------

            SessionService.revoke_all_sessions(
                user
            )

            # ------------------------------------------------
            # Email
            # ------------------------------------------------

            if send_email:

                EmailService.send_delete_email(
                    to_email=user_email,
                    reason=reason,
                    admin_email=request.user.email,
                )

            # ------------------------------------------------
            # Delete
            # ------------------------------------------------

            user.delete()

            return Response(
                {
                    "message": (
                        "User permanently deleted."
                    )
                },
                status=status.HTTP_200_OK,
            )

        # ====================================================
        # SOFT DELETE
        # ====================================================

        user.deleted_at = timezone.now()
        user.is_active = False

        user.save(
            update_fields=[
                "deleted_at",
                "is_active",
                "updated_at",
            ]
        )

        # ----------------------------------------------------
        # Revoke sessions
        # ----------------------------------------------------

        SessionService.revoke_all_sessions(
            user
        )

        # ----------------------------------------------------
        # Email
        # ----------------------------------------------------

        if send_email:

            EmailService.send_delete_email(
                to_email=user_email,
                reason=reason,
                admin_email=request.user.email,
            )

        return Response(
            {
                "message": "User deleted successfully."
            },
            status=status.HTTP_200_OK,
        )
