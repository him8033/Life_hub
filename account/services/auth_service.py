from django.contrib.auth import authenticate
from django.db import transaction
from django.utils import timezone
from account.models import User, UserRole, Role, UserStatus
from account.services.otp_service import OTPService
from account.services.jwt_service import JWTService
from account.services.session_service import SessionService
from account.services.status_service import StatusService
from account.models import LoginHistory
import re


class AuthService:
    """
    Core authentication service.
    Handles user registration, login, password management, and block/unblock operations.
    """

    @staticmethod
    def register_user(email, first_name, last_name, password, tc, ip_address=None, user_agent=None):
        """
        Register a new user with default role and status.

        Args:
            email: User email
            first_name: User first name
            last_name: User last name
            password: User password
            tc: Terms acceptance
            ip_address: IP address of registration
            user_agent: User agent string

        Returns:
            dict: Result with user instance if successful
        """
        try:
            # Create user using UserManager
            user = User.objects.create_user(
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password,
                tc=tc
            )

            # Generate and send OTP for email verification
            otp_result = OTPService.generate_otp(
                user=user,
                purpose_slug='email_verification',
                ip_address=ip_address,
                user_agent=user_agent
            )

            if not otp_result['success']:
                # Rollback user creation if OTP fails
                user.delete()
                return {
                    'success': False,
                    'error': f"Failed to send verification email: {otp_result['error']}"
                }

            return {
                'success': True,
                'user': user,
                'message': 'Registration successful. Please check your email for verification code.'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def authenticate_user(email, password, ip_address=None, user_agent=None):
        """
        Authenticate user with email and password.

        Args:
            email: User email
            password: User password
            ip_address: IP address of login attempt
            user_agent: User agent string

        Returns:
            dict: Result with user instance if successful
        """
        # Record login attempt
        login_method = 'email_password'
        success = False
        failure_reason = None

        try:
            # Authenticate using Django's authenticate
            user = authenticate(username=email, password=password)

            if not user:
                failure_reason = 'Invalid email or password'
                raise ValueError('Invalid credentials')

            # Check if user is blocked
            if user.is_blocked():
                failure_reason = 'Account is blocked'
                raise ValueError('Account is blocked')

            # Superusers bypass email verification
            if not user.is_superuser:
                # If an account has been activated (e.g. by an administrator), ensure email_verified is synchronized
                if user.status and user.status.slug == 'active' and not user.email_verified:
                    user.email_verified = True
                    user.email_verified_at = timezone.now()
                    user.save(update_fields=['email_verified', 'email_verified_at'])

                if not user.email_verified:
                    failure_reason = 'Please verify your email address before logging in'
                    raise ValueError(failure_reason)

                if user.status and user.status.slug == 'pending':
                    failure_reason = 'Account is pending activation. Please verify your email'
                    raise ValueError(failure_reason)

            # Check if user is active
            if not user.is_active:
                failure_reason = 'Account is inactive'
                raise ValueError('Account is inactive')

            # Check if user is soft deleted
            if user.deleted_at:
                failure_reason = 'Account has been deleted'
                raise ValueError('Account has been deleted')

            # Update last login info
            user.last_login = timezone.now()
            user.last_login_ip = ip_address
            user.save(update_fields=['last_login', 'last_login_ip'])

            success = True

            return {
                'success': True,
                'user': user,
                'message': 'Login successful'
            }

        except Exception as e:
            # Record failed login attempt
            try:
                user = User.objects.get(email=email)
                LoginHistory.objects.create(
                    user=user,
                    login_method=login_method,
                    success=success,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    failure_reason=failure_reason
                )
            except User.DoesNotExist:
                # Record failed attempt without user
                LoginHistory.objects.create(
                    user=None,
                    login_method=login_method,
                    success=success,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    failure_reason=failure_reason or 'User not found'
                )

            return {
                'success': False,
                'error': failure_reason or str(e)
            }

    @staticmethod
    def get_user_profile_data(user):
        """
        Build standardized user profile dictionary for auth responses.
        """
        roles_list = list(user.roles.values_list("slug", flat=True))
        primary_role = "admin" if "admin" in roles_list or user.is_superuser else (roles_list[0] if roles_list else "user")
        user_profile = {
            "user_id": user.user_id,
            "email": user.email,
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "full_name": user.full_name,
            "role": primary_role,
            "roles": roles_list,
            "is_superuser": user.is_superuser,
            "status": user.status.slug if user.status else "pending",
            "email_verified": user.email_verified,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }

        profile_image = None
        try:
            if hasattr(user, 'profile') and user.profile and user.profile.profile_image:
                profile_image = user.profile.profile_image.url
        except Exception:
            pass

        user_profile["profile_image"] = profile_image
        return user_profile

    @staticmethod
    def login_user(user, request=None, login_method='email_password'):
        """
        Complete login process by creating session and generating tokens.

        Args:
            user: User instance
            request: HTTP request object
            login_method: Login method string (e.g. 'email_password', 'email_verification')

        Returns:
            dict: Result with tokens and session info
        """
        try:
            # Generate JWT tokens
            tokens = JWTService.generate_tokens(user)

            # Create session
            session = SessionService.create_session(
                user=user,
                refresh_token=tokens['refresh'],
                request=request
            )

            # Record successful login
            device_info = SessionService._extract_device_info(
                request) if request else {}
            LoginHistory.objects.create(
                user=user,
                login_method=login_method,
                success=True,
                ip_address=device_info.get('ip'),
                user_agent=device_info.get('user_agent'),
                device=device_info.get('device'),
                browser=device_info.get('browser'),
                operating_system=device_info.get('os')
            )

            user_profile = AuthService.get_user_profile_data(user)

            return {
                'success': True,
                'tokens': tokens,
                'user': user_profile,
                'session': {
                    'session_id': session.usersession_id,
                    'device': session.device,
                    'browser': session.browser,
                    'expires_at': session.expires_at.isoformat() if session.expires_at else None
                }
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def change_password(user, old_password, new_password):
        """
        Change user password.

        Args:
            user: User instance
            old_password: Current password
            new_password: New password

        Returns:
            dict: Result
        """
        try:
            # Verify old password
            if not user.check_password(old_password):
                return {
                    'success': False,
                    'error': 'Current password is incorrect'
                }

            # Set new password
            user.set_password(new_password)
            user.save(update_fields=['password'])

            # Revoke all sessions except current
            # This would require tracking current session
            # For now, we revoke all sessions
            SessionService.revoke_all_sessions(user)

            return {
                'success': True,
                'message': 'Password changed successfully. All sessions have been revoked.'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def block_user(user_id, blocked_by, reason=None):
        """
        Block a user account.

        Args:
            user_id: User ID to block
            blocked_by: User ID who is blocking
            reason: Optional reason for blocking

        Returns:
            dict: Result
        """
        try:
            user = User.objects.get(user_id=user_id)
            blocked_status = UserStatus.objects.get(slug='blocked')

            # Update user status
            StatusService.update_user_status(user, 'blocked')

            # Revoke all sessions
            SessionService.revoke_all_sessions(user)

            return {
                'success': True,
                'message': 'User blocked successfully'
            }

        except User.DoesNotExist:
            return {
                'success': False,
                'error': 'User not found'
            }
        except UserStatus.DoesNotExist:
            return {
                'success': False,
                'error': 'Blocked status not found'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def unblock_user(user_id, unblocked_by, reason=None):
        """
        Unblock a user account.

        Args:
            user_id: User ID to unblock
            unblocked_by: User ID who is unblocking
            reason: Optional reason for unblocking

        Returns:
            dict: Result
        """
        try:
            user = User.objects.get(user_id=user_id)
            active_status = UserStatus.objects.get(slug='active')

            # Update user status
            StatusService.update_user_status(user, 'active')

            return {
                'success': True,
                'message': 'User unblocked successfully'
            }

        except User.DoesNotExist:
            return {
                'success': False,
                'error': 'User not found'
            }
        except UserStatus.DoesNotExist:
            return {
                'success': False,
                'error': 'Active status not found'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def assign_role(user_id, role_slug, assigned_by):
        """
        Assign a role to a user.

        Args:
            user_id: User ID
            role_slug: Role slug to assign
            assigned_by: User ID who is assigning

        Returns:
            dict: Result
        """
        try:
            user = User.objects.get(user_id=user_id)
            role = Role.objects.get(slug=role_slug)
            assigned_by_user = User.objects.get(user_id=assigned_by)

            # Check if user already has this role
            if UserRole.objects.filter(user=user, role=role).exists():
                return {
                    'success': False,
                    'error': 'User already has this role'
                }

            # Assign role
            UserRole.objects.create(
                user=user,
                role=role,
                assigned_by=assigned_by_user
            )

            return {
                'success': True,
                'message': 'Role assigned successfully'
            }

        except User.DoesNotExist:
            return {
                'success': False,
                'error': 'User not found'
            }
        except Role.DoesNotExist:
            return {
                'success': False,
                'error': 'Role not found'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def remove_role(user_id, role_slug):
        """
        Remove a role from a user.

        Args:
            user_id: User ID
            role_slug: Role slug to remove

        Returns:
            dict: Result
        """
        try:
            user = User.objects.get(user_id=user_id)
            role = Role.objects.get(slug=role_slug)

            # Remove role
            user_role = UserRole.objects.filter(user=user, role=role).first()
            if user_role:
                user_role.delete()
                return {
                    'success': True,
                    'message': 'Role removed successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'User does not have this role'
                }

        except User.DoesNotExist:
            return {
                'success': False,
                'error': 'User not found'
            }
        except Role.DoesNotExist:
            return {
                'success': False,
                'error': 'Role not found'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    @transaction.atomic
    def admin_change_password(
        user,
        new_password,
    ):
        """
        Change a user's password by an administrator.

        Does not require the user's old password.
        """

        try:
            user.set_password(new_password)

            user.save(
                update_fields=[
                    "password",
                    "updated_at",
                ]
            )

            return {
                "success": True,
                "error": None,
            }

        except Exception as e:

            return {
                "success": False,
                "error": str(e),
            }

    @staticmethod
    @transaction.atomic
    def admin_create_user(email, first_name, last_name, phone_number, password, roles, created_by):
        """
        Create a new user without OTP verification.
        User will be created with pending status by default.

        Args:
            email: User email
            first_name: User first name
            last_name: User last name
            phone_number: User phone number
            password: User password
            roles: List of role slugs to assign
            created_by: User instance of admin creating the user

        Returns:
            dict: Result with user instance if successful
        """
        try:
            # Create user using UserManager
            user = User.objects.create_user(
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password,
                tc=True  # Auto-accept terms for admin-created users
            )

            # Add phone number if provided
            if phone_number:
                user.phone_number = phone_number
                user.save(update_fields=['phone_number'])

            # Assign pending status (already done by create_user, but ensure it)
            pending_status = UserStatus.objects.get(slug='pending')
            user.status = pending_status
            user.save(update_fields=['status'])

            # Assign roles
            if roles:
                for role_slug in roles:
                    try:
                        role = Role.objects.get(slug=role_slug)
                        # Remove default user role if assigning specific roles
                        if role_slug != 'user':
                            UserRole.objects.filter(user=user, role__slug='user').delete()
                        
                        # Check if role already assigned
                        if not UserRole.objects.filter(user=user, role=role).exists():
                            UserRole.objects.create(user=user, role=role)
                    except Role.DoesNotExist:
                        # Skip invalid roles
                        continue

            return {
                'success': True,
                'user': user,
                'message': 'User created successfully with pending status'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
