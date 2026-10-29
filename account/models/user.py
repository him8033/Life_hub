from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.utils import timezone
from life_hub.utils import generate_ulid_with_prefix


# Custom User Manager
class UserManager(BaseUserManager):
    def create_user(self, email, first_name="", last_name="", tc=False, password=None, password2=None):
        """
        Creates and saves a User with the given email, name, tc and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            tc=tc,
        )

        user.set_password(password)
        user.save(using=self._db)
        
        # Assign default role and status after user is created
        from account.models import Role, UserStatus, UserRole
        try:
            default_role = Role.objects.get(slug='user')
            UserRole.objects.create(user=user, role=default_role)
        except Role.DoesNotExist:
            # Role will be created via data migration
            pass
        
        try:
            default_status = UserStatus.objects.get(slug='pending')
            user.status = default_status
            user.save(update_fields=['status'])
        except UserStatus.DoesNotExist:
            # Status will be created via data migration
            pass
        
        return user

    def create_superuser(self, email, first_name="", last_name="", tc=False, password=None):
        """
        Creates and saves a superuser with the given email, name, tc and password.
        """
        user = self.create_user(
            email,
            first_name=first_name,
            last_name=last_name,
            tc=tc,
            password=password,
        )
        
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        
        # Assign admin role
        from account.models import Role, UserRole, UserStatus
        try:
            admin_role = Role.objects.get(slug='admin')
            # Remove default user role if exists
            UserRole.objects.filter(user=user, role__slug='user').delete()
            UserRole.objects.create(user=user, role=admin_role)
            
            active_status = UserStatus.objects.get(slug='active')
            user.status = active_status
            user.email_verified = True
            user.email_verified_at = timezone.now()
            user.save(update_fields=['status', 'email_verified', 'email_verified_at'])
        except (Role.DoesNotExist, UserStatus.DoesNotExist):
            # Will be created via data migration
            pass
        
        return user


class User(AbstractBaseUser):
    # Primary identifiers
    id = models.BigAutoField(primary_key=True)
    user_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        editable=False
    )
    
    # Identity
    email = models.EmailField(
        verbose_name="Email",
        max_length=255,
        unique=True,
        db_index=True
    )
    first_name = models.CharField(max_length=100, null=True, blank=True, default="")
    last_name = models.CharField(max_length=100, null=True, blank=True, default="")
    phone_number = models.CharField(max_length=15, null=True, blank=True)

    # Authentication
    password = models.CharField(max_length=128)

    # Verification states
    email_verified = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    phone_verified = models.BooleanField(default=False)
    phone_verified_at = models.DateTimeField(null=True, blank=True)

    # Django authentication fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)

    # Terms acceptance
    tc = models.BooleanField(default=False)

    # Status (dynamic, replaces hardcoded role/status)
    status = models.ForeignKey(
        'account.UserStatus',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='users',
        db_index=True
    )

    # Security metadata
    last_login_ip = models.CharField(max_length=45, null=True, blank=True)
    last_seen = models.DateTimeField(null=True, blank=True)

    # Soft delete support
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["tc"]

    class Meta:
        db_table = 'account_user'
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['email']),
            models.Index(fields=['status']),
            models.Index(fields=['deleted_at']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.user_id:
            while True:
                candidate = generate_ulid_with_prefix("usr")
                if not User.objects.filter(user_id=candidate).exists():
                    self.user_id = candidate
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        """
        Does the user have a specific permission?
        This will be replaced with dynamic permission checking via PermissionService.
        """
        # For now, use superuser as fallback
        return self.is_superuser

    def has_module_perms(self, app_label):
        """
        Does the user have permissions to view the app `app_label`?
        This will be replaced with dynamic permission checking via PermissionService.
        """
        # For now, use superuser as fallback
        return self.is_superuser

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name or ''}".strip()

    @property
    def roles(self):
        """Get all roles for this user via UserRole relationship."""
        from account.models import UserRole
        role_ids = UserRole.objects.filter(user=self).values_list('role_id', flat=True)
        from account.models import Role
        return Role.objects.filter(id__in=role_ids)

    def has_role(self, role_slug):
        """Check if user has a specific role."""
        return self.roles.filter(slug=role_slug).exists()

    def has_permission(self, permission_slug):
        """
        Check if user has a specific permission via their roles.
        This will be enhanced with caching via PermissionService.
        """
        from account.models import RolePermission, Permission
        role_ids = self.roles.values_list('id', flat=True)
        permission_ids = RolePermission.objects.filter(
            role_id__in=role_ids
        ).values_list('permission_id', flat=True)
        return Permission.objects.filter(
            id__in=permission_ids,
            slug=permission_slug,
            is_active=True
        ).exists()

    def is_blocked(self):
        """Check if user is blocked based on status."""
        return self.status and self.status.slug in ['blocked', 'suspended', 'banned']

    def is_active_status(self):
        """Check if user has active status."""
        return self.status and self.status.slug == 'active'
