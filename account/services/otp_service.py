from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from account.models import OTP, OTPPurpose
from account.services.email_service import EmailService


class OTPService:
    """
    OTP generation and verification service.
    Handles OTP creation, validation, expiration, and resend cooldowns.
    """
    
    @staticmethod
    def generate_otp(user, purpose_slug, ip_address=None, user_agent=None):
        """
        Generate an OTP for a specific purpose.
        
        Args:
            user: User instance
            purpose_slug: Slug of the OTP purpose (e.g., 'email_verification')
            ip_address: IP address of the request
            user_agent: User agent string
            
        Returns:
            dict: Result with success status and OTP code if successful
        """
        try:
            # Get OTP purpose configuration
            purpose = OTPPurpose.objects.get(slug=purpose_slug, is_active=True)
        except OTPPurpose.DoesNotExist:
            return {
                'success': False,
                'error': 'Invalid OTP purpose'
            }
        
        # Check resend cooldown
        if not OTPService.can_resend_otp(user, purpose_slug):
            last_otp = OTP.objects.filter(
                user=user,
                purpose__slug=purpose_slug
            ).order_by('-created_at').first()
            
            if last_otp:
                cooldown_remaining = purpose.resend_cooldown_seconds - (
                    timezone.now() - last_otp.created_at
                ).total_seconds()
                return {
                    'success': False,
                    'error': 'Please wait before requesting another OTP',
                    'can_resend_after': int(cooldown_remaining)
                }
        
        # Invalidate previous OTPs for the same purpose
        OTP.objects.filter(
            user=user,
            purpose__slug=purpose_slug,
            is_used=False
        ).update(is_used=True)
        
        # Generate OTP code
        otp_code = OTP.generate_code()
        code_hash = OTP.hash_code(otp_code)
        
        # Calculate expiry time
        expires_at = timezone.now() + timedelta(seconds=purpose.expiry_seconds)
        
        # Create OTP record
        otp = OTP.objects.create(
            user=user,
            purpose=purpose,
            code_hash=code_hash,
            expires_at=expires_at,
            requested_ip=ip_address,
            requested_user_agent=user_agent
        )
        
        # Send OTP email
        email_sent = EmailService.send_otp_email(
            to_email=user.email,
            otp_code=otp_code,
            purpose=purpose_slug,
            expiry_minutes=purpose.expiry_seconds // 60
        )
        
        if not email_sent:
            # Delete OTP if email failed
            otp.delete()
            return {
                'success': False,
                'error': 'Failed to send OTP email'
            }
        
        return {
            'success': True,
            'otp_id': otp.otp_id,
            'expires_at': expires_at.isoformat() if expires_at else None,
            'expires_in': purpose.expiry_seconds
        }
    
    @staticmethod
    def verify_otp(user, purpose_slug, code):
        """
        Verify an OTP code.
        
        Args:
            user: User instance
            purpose_slug: Slug of the OTP purpose
            code: OTP code to verify
            
        Returns:
            dict: Result with success status
        """
        try:
            # Get OTP purpose
            purpose = OTPPurpose.objects.get(slug=purpose_slug, is_active=True)
        except OTPPurpose.DoesNotExist:
            return {
                'success': False,
                'error': 'Invalid OTP purpose'
            }
        
        # Find the most recent unused OTP for this user and purpose
        otp = OTP.objects.filter(
            user=user,
            purpose__slug=purpose_slug,
            is_used=False
        ).order_by('-created_at').first()
        
        if not otp:
            return {
                'success': False,
                'error': 'No valid OTP found. Please request a new OTP.'
            }
        
        # Check if OTP is expired
        if otp.is_expired():
            return {
                'success': False,
                'error': 'OTP has expired. Please request a new OTP.'
            }
        
        # Check if maximum attempts exceeded
        if otp.attempts >= purpose.max_attempts:
            otp.is_used = True
            otp.save(update_fields=['is_used'])
            return {
                'success': False,
                'error': 'Maximum verification attempts exceeded. Please request a new OTP.'
            }
        
        # Increment attempt counter
        otp.attempts += 1
        otp.save(update_fields=['attempts'])
        
        # Verify code
        if not otp.verify_code(code):
            attempts_remaining = max(0, purpose.max_attempts - otp.attempts)
            if otp.attempts >= purpose.max_attempts:
                otp.is_used = True
                otp.save(update_fields=['is_used'])
                return {
                    'success': False,
                    'error': 'Maximum verification attempts exceeded. Please request a new OTP.',
                    'attempts_remaining': 0
                }
            return {
                'success': False,
                'error': f'Invalid OTP code. {attempts_remaining} attempt{"s" if attempts_remaining != 1 else ""} remaining.',
                'attempts_remaining': attempts_remaining
            }
        
        # Mark OTP as used
        otp.is_used = True
        otp.used_at = timezone.now()
        otp.save(update_fields=['is_used', 'used_at'])
        
        return {
            'success': True,
            'message': 'OTP verified successfully'
        }
    
    @staticmethod
    def can_resend_otp(user, purpose_slug):
        """
        Check if user can request a new OTP (resend cooldown).
        
        Args:
            user: User instance
            purpose_slug: Slug of the OTP purpose
            
        Returns:
            bool: True if user can resend, False otherwise
        """
        try:
            purpose = OTPPurpose.objects.get(slug=purpose_slug, is_active=True)
        except OTPPurpose.DoesNotExist:
            return False
        
        # Get the most recent OTP for this user and purpose
        last_otp = OTP.objects.filter(
            user=user,
            purpose__slug=purpose_slug
        ).order_by('-created_at').first()
        
        if not last_otp:
            return True
        
        # Check if cooldown period has passed
        time_since_last_otp = timezone.now() - last_otp.created_at
        return time_since_last_otp.total_seconds() >= purpose.resend_cooldown_seconds
    
    @staticmethod
    def invalidate_user_otps(user, purpose_slug=None):
        """
        Invalidate all OTPs for a user (optionally for a specific purpose).
        
        Args:
            user: User instance
            purpose_slug: Optional purpose slug to filter
        """
        queryset = OTP.objects.filter(user=user, is_used=False)
        
        if purpose_slug:
            queryset = queryset.filter(purpose__slug=purpose_slug)
        
        queryset.update(is_used=True)
    
    @staticmethod
    def cleanup_expired_otps():
        """
        Clean up expired OTPs (can be called periodically).
        This is a maintenance operation.
        """
        expired_otps = OTP.objects.filter(
            expires_at__lt=timezone.now(),
            is_used=False
        )
        count = expired_otps.count()
        expired_otps.update(is_used=True)
        return count