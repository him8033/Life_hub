from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from account.models import UserSession
from life_hub.utils import generate_ulid_with_prefix, get_client_ip
import re


class SessionService:
    """
    User session management service.
    Handles session creation, revocation, and activity tracking.
    """
    
    @staticmethod
    def create_session(user, refresh_token, request=None):
        """
        Create a new user session.
        
        Args:
            user: User instance
            refresh_token: JWT refresh token
            request: HTTP request object (optional)
            
        Returns:
            UserSession: Created session instance
        """
        # Extract device information
        device_info = SessionService._extract_device_info(request) if request else {}
        
        # Generate session identifier
        session_identifier = generate_ulid_with_prefix("sess")
        
        # Calculate expiry time (from JWT settings)
        from rest_framework_simplejwt.settings import api_settings
        expires_at = timezone.now() + api_settings.REFRESH_TOKEN_LIFETIME
        
        # Create session
        session = UserSession.objects.create(
            user=user,
            session_identifier=session_identifier,
            refresh_token_hash=UserSession.hash_refresh_token(refresh_token),
            device=device_info.get('device'),
            browser=device_info.get('browser'),
            operating_system=device_info.get('os'),
            ip_address=device_info.get('ip'),
            user_agent=device_info.get('user_agent'),
            expires_at=expires_at
        )
        
        return session
    
    @staticmethod
    def _extract_device_info(request):
        """
        Extract device information from request.

        Args:
            request: HTTP request object

        Returns:
            dict: Device information
        """
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        ip_address = get_client_ip(request)

        # Enhanced device detection
        device = 'desktop'  # Default
        browser = 'unknown'
        operating_system = 'unknown'

        # More accurate mobile detection
        # Check for mobile-specific indicators first
        mobile_indicators = [
            'Android', 'iPhone', 'iPad', 'iPod', 'BlackBerry',
            'IEMobile', 'Opera Mini', 'Mobile Safari'
        ]

        # Only classify as mobile if it's clearly a mobile device
        is_mobile = False
        for indicator in mobile_indicators:
            if indicator in user_agent:
                is_mobile = True
                break

        # Additional check: Android but not a tablet
        if 'Android' in user_agent and 'Mobile' in user_agent:
            is_mobile = True
        elif 'Android' in user_agent and 'Mobile' not in user_agent:
            # Android tablet
            device = 'tablet'
            is_mobile = False

        # iPad is a tablet, not mobile
        if 'iPad' in user_agent:
            device = 'tablet'
            is_mobile = False

        if is_mobile:
            device = 'mobile'

        # Detect browser
        if 'Edg/' in user_agent:
            browser = 'Edge'
        elif 'Chrome/' in user_agent and 'Edg/' not in user_agent:
            browser = 'Chrome'
        elif 'Firefox/' in user_agent:
            browser = 'Firefox'
        elif 'Safari/' in user_agent and 'Chrome/' not in user_agent and 'Edg/' not in user_agent:
            browser = 'Safari'
        elif 'Opera/' in user_agent or 'OPR/' in user_agent:
            browser = 'Opera'
        elif 'Brave/' in user_agent:
            browser = 'Brave'

        # Detect OS
        if 'Windows NT' in user_agent:
            operating_system = 'Windows'
        elif 'Mac OS X' in user_agent or 'macOS' in user_agent:
            operating_system = 'macOS'
        elif 'Linux' in user_agent and 'Android' not in user_agent:
            operating_system = 'Linux'
        elif 'Android' in user_agent:
            operating_system = 'Android'
        elif 'iOS' in user_agent or 'iPhone' in user_agent:
            operating_system = 'iOS'
        elif 'iPad' in user_agent:
            operating_system = 'iPadOS'

        return {
            'device': device,
            'browser': browser,
            'os': operating_system,
            'ip': ip_address,
            'user_agent': user_agent
        }
    
    @staticmethod
    def get_user_sessions(user):
        """
        Get all active sessions for a user.
        
        Args:
            user: User instance
            
        Returns:
            QuerySet: Active user sessions
        """
        return UserSession.objects.filter(
            user=user,
            is_active=True,
            expires_at__gt=timezone.now()
        ).order_by('-last_activity_at')
    
    @staticmethod
    def get_session(session_id):
        """
        Get a specific session by ID.
        
        Args:
            session_id: Session ID
            
        Returns:
            UserSession or None
        """
        try:
            return UserSession.objects.get(
                usersession_id=session_id,
                is_active=True
            )
        except UserSession.DoesNotExist:
            return None
    
    @staticmethod
    def validate_session(session_id, refresh_token):
        """
        Validate a session with refresh token.
        
        Args:
            session_id: Session ID
            refresh_token: Refresh token to validate
            
        Returns:
            dict: Validation result
        """
        session = SessionService.get_session(session_id)
        
        if not session:
            return {
                'valid': False,
                'reason': 'Session not found'
            }
        
        if session.is_expired():
            session.revoke('expired')
            return {
                'valid': False,
                'reason': 'Session expired'
            }
        
        if session.is_revoked():
            return {
                'valid': False,
                'reason': 'Session revoked'
            }
        
        # Validate refresh token hash
        if session.refresh_token_hash != UserSession.hash_refresh_token(refresh_token):
            return {
                'valid': False,
                'reason': 'Invalid token'
            }
        
        return {
            'valid': True,
            'session': session
        }
    
    @staticmethod
    def revoke_session(session_id, reason=None):
        """
        Revoke a specific session.
        
        Args:
            session_id: Session ID
            reason: Optional reason for revocation
            
        Returns:
            bool: True if revoked successfully
        """
        session = SessionService.get_session(session_id)
        if session:
            session.revoke(reason)
            return True
        return False
    
    @staticmethod
    def revoke_all_sessions(user, except_session_id=None):
        """
        Revoke all sessions for a user.
        
        Args:
            user: User instance
            except_session_id: Optional session ID to exclude from revocation
            
        Returns:
            int: Number of sessions revoked
        """
        queryset = UserSession.objects.filter(
            user=user,
            is_active=True
        )
        
        if except_session_id:
            queryset = queryset.exclude(usersession_id=except_session_id)
        
        count = queryset.count()
        queryset.update(
            is_active=False,
            revoked_at=timezone.now(),
            revoked_reason='logout_all'
        )
        
        return count
    
    @staticmethod
    def update_activity(session_id):
        """
        Update session activity timestamp.
        
        Args:
            session_id: Session ID
            
        Returns:
            bool: True if updated successfully
        """
        session = SessionService.get_session(session_id)
        if session:
            session.update_activity()
            return True
        return False
    
    @staticmethod
    def cleanup_expired_sessions():
        """
        Clean up expired sessions (maintenance operation).
        
        Returns:
            int: Number of sessions cleaned up
        """
        expired_sessions = UserSession.objects.filter(
            expires_at__lt=timezone.now(),
            is_active=True
        )
        count = expired_sessions.count()
        expired_sessions.update(
            is_active=False,
            revoked_at=timezone.now(),
            revoked_reason='expired'
        )
        return count
    
    @staticmethod
    def get_session_count(user):
        """
        Get count of active sessions for a user.
        
        Args:
            user: User instance
            
        Returns:
            int: Number of active sessions
        """
        return UserSession.objects.filter(
            user=user,
            is_active=True,
            expires_at__gt=timezone.now()
        ).count()