"""
Session Validation Views
Handles session validation for frontend API interceptor
"""

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
import logging

from account.models import UserSession

logger = logging.getLogger(__name__)


class SessionValidationView(APIView):
    """
    Validate current session status

    POST /api/v1/accounts/sessions/validate/
    Request body: { "session_id": "uss_abc123..." }
    Response: { "success": true/false, "data": { "is_valid": true/false, "reason": "..." } }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        session_id = request.data.get('session_id')
        user = request.user

        if not session_id:
            logger.warning(f"Session validation failed - No session_id provided for user: {user.email}")
            return Response({
                'success': False,
                'message': 'Session ID is required',
                'data': {'is_valid': False, 'reason': 'missing_session_id'}
            }, status=400)

        try:
            session = UserSession.objects.get(
                usersession_id=session_id,
                user=user
            )

            # Check if session is revoked
            if session.is_revoked():
                logger.warning(f"Session validation failed - Session revoked: {session.usersession_id} for user: {user.email}")
                return Response({
                    'success': False,
                    'message': 'Session has been revoked by an administrator',
                    'data': {'is_valid': False, 'reason': 'revoked'}
                }, status=401)

            # Check if session is inactive
            if not session.is_active:
                logger.warning(f"Session validation failed - Session inactive: {session.usersession_id} for user: {user.email}")
                return Response({
                    'success': False,
                    'message': 'Session is inactive',
                    'data': {'is_valid': False, 'reason': 'inactive'}
                }, status=401)

            # Check if session is expired
            if session.is_expired():
                logger.warning(f"Session validation failed - Session expired: {session.usersession_id} for user: {user.email}")
                return Response({
                    'success': False,
                    'message': 'Session has expired',
                    'data': {'is_valid': False, 'reason': 'expired'}
                }, status=401)

            # Update last activity timestamp
            session.last_activity_at = timezone.now()
            session.save(update_fields=['last_activity_at'])

            return Response({
                'success': True,
                'message': 'Session is valid',
                'data': {
                    'is_valid': True,
                    'session_id': session.usersession_id,
                    'user_id': session.user.user_id,
                    'expires_at': session.expires_at.isoformat()
                }
            })

        except UserSession.DoesNotExist:
            logger.warning(f"Session validation failed - Session not found: {session_id} for user: {user.email}")
            # Log all sessions for this user for debugging
            user_sessions = UserSession.objects.filter(user=user)
            logger.info(f"User {user.email} has {user_sessions.count()} sessions in database")
            for sess in user_sessions:
                logger.info(f"  - Session: {sess.usersession_id}, Active: {sess.is_active}, Revoked: {sess.is_revoked()}, Expires: {sess.expires_at}")

            return Response({
                'success': False,
                'message': 'Session not found',
                'data': {'is_valid': False, 'reason': 'not_found'}
            }, status=401)
