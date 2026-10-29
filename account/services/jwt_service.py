from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.settings import api_settings
from django.utils import timezone
from datetime import timedelta
from account.models import User
import secrets


class JWTService:
    """
    JWT token management service with token rotation support.
    Handles token generation, validation, and refresh with rotation.
    """

    @staticmethod
    def generate_tokens(user):
        """
        Generate JWT access and refresh tokens for a user.

        Args:
            user: User instance

        Returns:
            dict: Dictionary containing access and refresh tokens
        """
        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    @staticmethod
    def refresh_tokens(refresh_token):
        """
        Refresh tokens with rotation (new refresh token on each refresh).

        Args:
            refresh_token: Existing refresh token

        Returns:
            dict: Result with new tokens if successful
        """
        try:
            refresh = RefreshToken(refresh_token)

            # Check if token rotation is enabled in settings
            if api_settings.ROTATE_REFRESH_TOKENS:
                from account.models import User
                user_id = refresh.get(api_settings.USER_ID_CLAIM, refresh.get('user_id'))
                try:
                    user = User.objects.get(id=user_id)
                except User.DoesNotExist:
                    return {
                        'success': False,
                        'error': 'User not found'
                    }

                # Rotate the refresh token
                new_refresh = RefreshToken.for_user(user)

                # Blacklist old token if enabled
                if api_settings.BLACKLIST_AFTER_ROTATION:
                    try:
                        refresh.blacklist()
                    except (AttributeError, Exception):
                        # Blacklist app not installed or error
                        pass

                return {
                    'success': True,
                    'access': str(new_refresh.access_token),
                    'refresh': str(new_refresh),
                }
            else:
                # No rotation, just return new access token
                return {
                    'success': True,
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def validate_token(token):
        """
        Validate a JWT token.

        Args:
            token: JWT token string

        Returns:
            bool: True if token is valid, False otherwise
        """
        try:
            AccessToken(token)
            return True
        except Exception:
            return False

    @staticmethod
    def get_user_from_token(token):
        """
        Extract user from JWT token.

        Args:
            token: JWT token string

        Returns:
            User instance or None if invalid
        """
        try:
            access_token = AccessToken(token)
            user_id = access_token[api_settings.USER_ID_CLAIM]
            from account.models import User
            return User.objects.get(id=user_id)
        except Exception:
            return None

    @staticmethod
    def get_token_expiry(token):
        """
        Get token expiry time.

        Args:
            token: JWT token string

        Returns:
            datetime: Expiry time or None if invalid
        """
        try:
            access_token = AccessToken(token)
            return timezone.now() + api_settings.ACCESS_TOKEN_LIFETIME
        except Exception:
            return None

    @staticmethod
    def blacklist_token(token):
        """
        Blacklist a token (requires rest_framework_simplejwt.token_blacklist app).

        Args:
            token: JWT token string

        Returns:
            bool: True if blacklisted successfully, False otherwise
        """
        try:
            from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
            from rest_framework_simplejwt.tokens import RefreshToken

            refresh = RefreshToken(token)
            blacklisted_token = BlacklistedToken.objects.create(token=refresh)
            return True
        except Exception:
            # Blacklist app not installed or other error
            return False

    @staticmethod
    def is_token_blacklisted(token):
        """
        Check if a token is blacklisted.

        Args:
            token: JWT token string

        Returns:
            bool: True if blacklisted, False otherwise
        """
        try:
            from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
            from rest_framework_simplejwt.tokens import RefreshToken

            refresh = RefreshToken(token)
            return BlacklistedToken.objects.filter(token=refresh).exists()
        except Exception:
            # Blacklist app not installed
            return False

    @staticmethod
    def revoke_user_tokens(user):
        """
        Revoke all tokens for a user by blacklisting them.
        This requires the token_blacklist app.

        Args:
            user: User instance

        Returns:
            int: Number of tokens revoked
        """
        try:
            from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken

            # This is a simplified approach
            # In production, you'd need to track active tokens
            # For now, we revoke all user sessions instead
            from account.services.session_service import SessionService
            SessionService.revoke_all_sessions(user)

            return 0
        except Exception:
            return 0

    @staticmethod
    def generate_password_reset_token(user, email):
        """
        Generate a secure random token for password reset flow.
        Stored in database for single-use validation.

        Args:
            user: User instance
            email: User email for validation

        Returns:
            str: Secure random token (single-use)
        """
        from account.models import PasswordResetToken

        # Generate secure random token
        token = secrets.token_urlsafe(32)

        # Store in database
        PasswordResetToken.objects.create(
            user=user,
            email=email,
            token=token,
            token_type='request',
            expires_at=timezone.now() + timedelta(minutes=15)
        )

        return token

    @staticmethod
    def generate_password_reset_confirm_token(user, email):
        """
        Generate a secure random token for password reset confirmation.
        Stored in database for single-use validation.

        Args:
            user: User instance
            email: User email for validation

        Returns:
            str: Secure random token (single-use)
        """
        from account.models import PasswordResetToken

        # Generate secure random token
        token = secrets.token_urlsafe(32)

        # Store in database
        PasswordResetToken.objects.create(
            user=user,
            email=email,
            token=token,
            token_type='confirm',
            expires_at=timezone.now() + timedelta(minutes=15)
        )

        return token

    @staticmethod
    def validate_password_reset_token(token, expected_type, mark_as_used=False):
        """
        Validate a password reset token from database.
        Optionally marks token as used after validation (single-use).

        Args:
            token: Token string
            expected_type: Expected token type ('request' or 'confirm')
            mark_as_used: Whether to mark the token as used (default: False)

        Returns:
            dict: Result with user_id and email if valid, error otherwise
        """
        from account.models import PasswordResetToken

        try:
            reset_token = PasswordResetToken.objects.get(
                token=token,
                token_type=expected_type,
                is_used=False,
                expires_at__gt=timezone.now()
            )

            # Only mark as used if explicitly requested
            if mark_as_used:
                reset_token.is_used = True
                reset_token.used_at = timezone.now()
                reset_token.save(update_fields=['is_used', 'used_at'])

            return {
                'valid': True,
                'user_id': reset_token.user.id,
                'email': reset_token.email,
            }

        except PasswordResetToken.DoesNotExist:
            return {
                'valid': False,
                'error': 'Invalid or expired token'
            }
        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }
