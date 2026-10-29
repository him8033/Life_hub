from django.core.cache import cache
from account.models import User, UserStatus
from django.utils import timezone


class StatusService:
    """
    User status management service.
    Handles status validation, transitions, and semantic status checks.
    """
    
    # Cache timeout (in seconds)
    CACHE_TIMEOUT = 300  # 5 minutes
    
    @staticmethod
    def update_user_status(user, status_slug):
        """
        Update user's status.
        
        Args:
            user: User instance
            status_slug: New status slug
            
        Returns:
            bool: True if updated successfully
        """
        try:
            status = UserStatus.objects.get(slug=status_slug, is_active=True)
            user.status = status
            update_fields = ['status']
            if status_slug == 'active' and not user.email_verified:
                user.email_verified = True
                user.email_verified_at = timezone.now()
                update_fields.extend(['email_verified', 'email_verified_at'])
            user.save(update_fields=update_fields)
            
            # Clear status cache
            StatusService.clear_user_status_cache(user)
            
            return True
        except UserStatus.DoesNotExist:
            return False
    
    @staticmethod
    def get_user_status(user):
        """
        Get user's current status.
        
        Args:
            user: User instance
            
        Returns:
            UserStatus or None
        """
        return user.status
    
    @staticmethod
    def is_user_active(user):
        """
        Check if user has active status.
        
        Args:
            user: User instance
            
        Returns:
            bool: True if user is active
        """
        # Check cache first
        cache_key = f"user_status_{user.user_id}"
        cached_status = cache.get(cache_key)
        
        if cached_status is not None:
            return cached_status == 'active'
        
        # Get from database
        status = StatusService.get_user_status(user)
        is_active = status and status.slug == 'active'
        
        # Cache the result
        cache.set(cache_key, status.slug if status else None, StatusService.CACHE_TIMEOUT)
        
        return is_active
    
    @staticmethod
    def is_user_blocked(user):
        """
        Check if user is blocked.
        
        Args:
            user: User instance
            
        Returns:
            bool: True if user is blocked
        """
        status = StatusService.get_user_status(user)
        return status and status.slug in ['blocked', 'suspended', 'banned']
    
    @staticmethod
    def is_user_pending(user):
        """
        Check if user has pending status.
        
        Args:
            user: User instance
            
        Returns:
            bool: True if user is pending
        """
        status = StatusService.get_user_status(user)
        return status and status.slug == 'pending'
    
    @staticmethod
    def is_user_deleted(user):
        """
        Check if user is soft deleted.
        
        Args:
            user: User instance
            
        Returns:
            bool: True if user is deleted
        """
        return user.deleted_at is not None
    
    @staticmethod
    def can_user_authenticate(user):
        """
        Check if user can authenticate (not blocked or deleted).
        
        Args:
            user: User instance
            
        Returns:
            bool: True if user can authenticate
        """
        return (
            user.is_active and
            not StatusService.is_user_blocked(user) and
            not StatusService.is_user_deleted(user)
        )
    
    @staticmethod
    def clear_user_status_cache(user):
        """
        Clear cached status for a user.
        
        Args:
            user: User instance
        """
        cache_key = f"user_status_{user.user_id}"
        cache.delete(cache_key)
    
    @staticmethod
    def get_status_by_slug(status_slug):
        """
        Get status by slug.
        
        Args:
            status_slug: Status slug
            
        Returns:
            UserStatus or None
        """
        try:
            return UserStatus.objects.get(slug=status_slug, is_active=True)
        except UserStatus.DoesNotExist:
            return None
    
    @staticmethod
    def get_all_active_statuses():
        """
        Get all active statuses.
        
        Returns:
            QuerySet: UserStatus queryset
        """
        return UserStatus.objects.filter(is_active=True).order_by('name')
    
    @staticmethod
    def create_status(name, slug, description=None):
        """
        Create a new user status.
        
        Args:
            name: Status name
            slug: Status slug
            description: Optional description
            
        Returns:
            UserStatus or None
        """
        try:
            return UserStatus.objects.create(
                name=name,
                slug=slug,
                description=description,
                is_active=True
            )
        except Exception:
            return None
    
    @staticmethod
    def activate_user(user):
        """
        Activate a user account.
        
        Args:
            user: User instance
            
        Returns:
            bool: True if activated successfully
        """
        return StatusService.update_user_status(user, 'active')
    
    @staticmethod
    def deactivate_user(user):
        """
        Deactivate a user account (set to suspended).
        
        Args:
            user: User instance
            
        Returns:
            bool: True if deactivated successfully
        """
        return StatusService.update_user_status(user, 'suspended')
    
    @staticmethod
    def soft_delete_user(user):
        """
        Soft delete a user account.
        
        Args:
            user: User instance
            
        Returns:
            bool: True if deleted successfully
        """
        user.deleted_at = timezone.now()
        user.save(update_fields=['deleted_at'])
        StatusService.update_user_status(user, 'deleted')
        return True
    
    @staticmethod
    def restore_user(user):
        """
        Restore a soft-deleted user account.
        
        Args:
            user: User instance
            
        Returns:
            bool: True if restored successfully
        """
        user.deleted_at = None
        user.save(update_fields=['deleted_at'])
        StatusService.update_user_status(user, 'active')
        return True