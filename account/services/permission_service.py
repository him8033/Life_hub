from django.core.cache import cache
from account.models import User, Role, Permission, UserRole, RolePermission


class PermissionService:
    """
    Permission checking service with caching support.
    Handles user permission validation and role-based access control.
    """
    
    # Cache timeout (in seconds)
    CACHE_TIMEOUT = 300  # 5 minutes
    
    @staticmethod
    def user_has_permission(user, permission_slug):
        """
        Check if user has a specific permission.
        
        Args:
            user: User instance
            permission_slug: Permission slug to check
            
        Returns:
            bool: True if user has permission
        """
        # Superusers have all permissions
        if user.is_superuser:
            return True
        
        # Check cache first
        cache_key = f"user_permissions_{user.user_id}"
        cached_permissions = cache.get(cache_key)
        
        if cached_permissions is None:
            # Get user's permissions from database
            cached_permissions = PermissionService.get_user_permissions(user)
            cache.set(cache_key, cached_permissions, PermissionService.CACHE_TIMEOUT)
        
        return permission_slug in cached_permissions
    
    @staticmethod
    def user_has_any_permission(user, permission_slugs):
        """
        Check if user has any of the specified permissions.
        
        Args:
            user: User instance
            permission_slugs: List of permission slugs
            
        Returns:
            bool: True if user has any of the permissions
        """
        return any(PermissionService.user_has_permission(user, slug) for slug in permission_slugs)
    
    @staticmethod
    def user_has_all_permissions(user, permission_slugs):
        """
        Check if user has all of the specified permissions.
        
        Args:
            user: User instance
            permission_slugs: List of permission slugs
            
        Returns:
            bool: True if user has all permissions
        """
        return all(PermissionService.user_has_permission(user, slug) for slug in permission_slugs)
    
    @staticmethod
    def get_user_permissions(user):
        """
        Get all permissions for a user.
        
        Args:
            user: User instance
            
        Returns:
            set: Set of permission slugs
        """
        # Superusers have all permissions
        if user.is_superuser:
            all_permissions = Permission.objects.filter(is_active=True).values_list('slug', flat=True)
            return set(all_permissions)
        
        # Get user's roles
        role_ids = UserRole.objects.filter(user=user).values_list('role_id', flat=True)
        
        # Get permissions for user's roles
        permission_ids = RolePermission.objects.filter(
            role_id__in=role_ids
        ).values_list('permission_id', flat=True)
        
        # Get active permissions
        permissions = Permission.objects.filter(
            id__in=permission_ids,
            is_active=True
        ).values_list('slug', flat=True)
        
        return set(permissions)
    
    @staticmethod
    def get_role_permissions(role_id):
        """
        Get all permissions for a role.
        
        Args:
            role_id: Role ID
            
        Returns:
            QuerySet: Permission queryset
        """
        try:
            role = Role.objects.get(role_id=role_id)
            permission_ids = RolePermission.objects.filter(role=role).values_list('permission_id', flat=True)
            return Permission.objects.filter(id__in=permission_ids, is_active=True)
        except Role.DoesNotExist:
            return Permission.objects.none()
    
    @staticmethod
    def clear_user_permission_cache(user):
        """
        Clear cached permissions for a user.
        
        Args:
            user: User instance
        """
        cache_key = f"user_permissions_{user.user_id}"
        cache.delete(cache_key)
    
    @staticmethod
    def assign_permission_to_role(role_id, permission_id):
        """
        Assign a permission to a role.
        
        Args:
            role_id: Role ID
            permission_id: Permission ID
            
        Returns:
            bool: True if assigned successfully
        """
        try:
            role = Role.objects.get(role_id=role_id)
            permission = Permission.objects.get(permission_id=permission_id)
            
            RolePermission.objects.get_or_create(
                role=role,
                permission=permission
            )
            
            # Clear cache for all users with this role
            user_ids = UserRole.objects.filter(role=role).values_list('user_id', flat=True)
            for user_id in user_ids:
                try:
                    user = User.objects.get(user_id=user_id)
                    PermissionService.clear_user_permission_cache(user)
                except User.DoesNotExist:
                    continue
            
            return True
            
        except (Role.DoesNotExist, Permission.DoesNotExist):
            return False
    
    @staticmethod
    def remove_permission_from_role(role_id, permission_id):
        """
        Remove a permission from a role.
        
        Args:
            role_id: Role ID
            permission_id: Permission ID
            
        Returns:
            bool: True if removed successfully
        """
        try:
            role = Role.objects.get(role_id=role_id)
            permission = Permission.objects.get(permission_id=permission_id)
            
            RolePermission.objects.filter(role=role, permission=permission).delete()
            
            # Clear cache for all users with this role
            user_ids = UserRole.objects.filter(role=role).values_list('user_id', flat=True)
            for user_id in user_ids:
                try:
                    user = User.objects.get(user_id=user_id)
                    PermissionService.clear_user_permission_cache(user)
                except User.DoesNotExist:
                    continue
            
            return True
            
        except (Role.DoesNotExist, Permission.DoesNotExist):
            return False
    
    @staticmethod
    def get_users_with_permission(permission_slug):
        """
        Get all users who have a specific permission.
        
        Args:
            permission_slug: Permission slug
            
        Returns:
            QuerySet: User queryset
        """
        try:
            permission = Permission.objects.get(slug=permission_slug, is_active=True)
            role_ids = RolePermission.objects.filter(permission=permission).values_list('role_id', flat=True)
            user_ids = UserRole.objects.filter(role_id__in=role_ids).values_list('user_id', flat=True)
            return User.objects.filter(user_id__in=user_ids)
        except Permission.DoesNotExist:
            return User.objects.none()
    
    @staticmethod
    def check_module_permission(user, module, action):
        """
        Check if user has permission for a specific module action.
        
        Args:
            user: User instance
            module: Module name (e.g., 'user', 'portfolio')
            action: Action name (e.g., 'create', 'read', 'update', 'delete')
            
        Returns:
            bool: True if user has permission
        """
        permission_slug = f"{module}.{action}"
        return PermissionService.user_has_permission(user, permission_slug)