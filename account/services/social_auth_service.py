from django.db import transaction
from django.utils import timezone
from account.models import User, SocialAccount, SocialProvider, UserRole, Role, UserStatus
from account.services.jwt_service import JWTService
from account.services.session_service import SessionService
from account.services.status_service import StatusService
from account.models import LoginHistory


class SocialAuthService:
    """
    Social authentication service with provider abstraction.
    Handles Google, GitHub, and future social providers.
    """
    
    @staticmethod
    def authenticate_google(id_token, request=None):
        """
        Authenticate user with Google OAuth.
        
        Args:
            id_token: Google ID token
            request: HTTP request object
            
        Returns:
            dict: Result with user and tokens if successful
        """
        try:
            import os
            import requests

            idinfo = None
            try:
                from google.oauth2 import id_token as google_id_token
                from google.auth.transport import requests as google_requests
                client_id = os.environ.get('GOOGLE_OAUTH_CLIENT_ID')
                idinfo = google_id_token.verify_oauth2_token(
                    id_token,
                    google_requests.Request(),
                    audience=client_id
                )
            except Exception:
                # Direct verification with Google tokeninfo endpoint
                resp = requests.get(
                    f'https://oauth2.googleapis.com/tokeninfo?id_token={id_token}',
                    timeout=10
                )
                if resp.status_code == 200:
                    idinfo = resp.json()
                    expected_aud = os.environ.get('GOOGLE_OAUTH_CLIENT_ID')
                    if expected_aud and idinfo.get('aud') != expected_aud:
                        return {'success': False, 'error': 'Invalid Google token audience'}
                else:
                    return {'success': False, 'error': 'Failed to verify Google ID token'}

            email = idinfo.get('email')
            if not email:
                return {'success': False, 'error': 'Google account email not found'}

            provider_user_id = str(idinfo.get('sub'))
            first_name = idinfo.get('given_name', '')
            last_name = idinfo.get('family_name', '')
            avatar_url = idinfo.get('picture')

            user, created = SocialAuthService._find_or_create_user(
                provider_slug='google',
                provider_user_id=provider_user_id,
                email=email,
                first_name=first_name,
                last_name=last_name,
                avatar_url=avatar_url
            )

            login_result = SocialAuthService.complete_social_login(user, request)
            login_result['is_new_user'] = created
            return login_result

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def authenticate_github(code, request=None):
        """
        Authenticate user with GitHub OAuth.
        
        Args:
            code: GitHub authorization code
            request: HTTP request object
            
        Returns:
            dict: Result with user and tokens if successful
        """
        try:
            import os
            import requests

            client_id = os.environ.get('GITHUB_OAUTH_CLIENT_ID')
            client_secret = os.environ.get('GITHUB_OAUTH_CLIENT_SECRET')

            response = requests.post(
                'https://github.com/login/oauth/access_token',
                data={
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'code': code
                },
                headers={'Accept': 'application/json'},
                timeout=10
            )

            token_data = response.json()
            access_token = token_data.get('access_token')
            if not access_token:
                return {
                    'success': False,
                    'error': token_data.get('error_description', 'Failed to obtain GitHub access token')
                }

            user_response = requests.get(
                'https://api.github.com/user',
                headers={'Authorization': f'Bearer {access_token}'},
                timeout=10
            )
            if user_response.status_code != 200:
                return {'success': False, 'error': 'Failed to fetch GitHub profile'}

            github_user = user_response.json()
            provider_user_id = str(github_user.get('id'))
            email = github_user.get('email')
            if not email:
                emails_resp = requests.get(
                    'https://api.github.com/user/emails',
                    headers={'Authorization': f'Bearer {access_token}'},
                    timeout=10
                )
                if emails_resp.status_code == 200:
                    for em in emails_resp.json():
                        if em.get('primary') and em.get('verified'):
                            email = em.get('email')
                            break

            username = github_user.get('login', '')
            name = (github_user.get('name') or username).split()
            first_name = name[0] if name else 'GitHub'
            last_name = name[1] if len(name) > 1 else 'User'
            avatar_url = github_user.get('avatar_url')

            user, created = SocialAuthService._find_or_create_user(
                provider_slug='github',
                provider_user_id=provider_user_id,
                email=email or f"{username}@github.user",
                first_name=first_name,
                last_name=last_name,
                avatar_url=avatar_url,
                username=username
            )

            login_result = SocialAuthService.complete_social_login(user, request)
            login_result['is_new_user'] = created
            return login_result

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def _find_or_create_user(provider_slug, provider_user_id, email, first_name, last_name, avatar_url=None, username=None):
        """
        Find existing user or create new one from social provider data.
        
        Args:
            provider_slug: Provider slug (e.g., 'google', 'github')
            provider_user_id: Provider's user ID
            email: User email from provider
            first_name: User first name
            last_name: User last name
            avatar_url: User avatar URL
            username: Optional provider username
            
        Returns:
            tuple: (User instance, bool indicating if user was created)
        """
        try:
            # Check if social account already exists
            provider = SocialProvider.objects.get(slug=provider_slug)
            social_account = SocialAccount.objects.filter(
                provider=provider,
                provider_user_id=provider_user_id
            ).first()
            
            if social_account:
                # User already exists, return it
                return social_account.user, False
            
            # Check if user with same email exists
            existing_user = None
            if email:
                existing_user = User.objects.filter(email=email).first()
            
            if existing_user:
                # Link social account to existing user
                SocialAuthService._link_social_account(
                    user=existing_user,
                    provider=provider,
                    provider_user_id=provider_user_id,
                    email=email,
                    username=username or email,
                    avatar_url=avatar_url
                )
                return existing_user, False
            
            # Create new user
            with transaction.atomic():
                user = User.objects.create_user(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=None,  # No password for social auth users
                    tc=True  # Auto-accept terms for social auth
                )
                
                # Social auth users are considered email verified
                user.email_verified = True
                user.email_verified_at = timezone.now()
                user.save(update_fields=['email_verified', 'email_verified_at'])
                
                # Set active status
                StatusService.update_user_status(user, 'active')
                
                # Link social account
                SocialAuthService._link_social_account(
                    user=user,
                    provider=provider,
                    provider_user_id=provider_user_id,
                    email=email,
                    username=username or email,
                    avatar_url=avatar_url
                )
                
                return user, True
                
        except SocialProvider.DoesNotExist:
            raise ValueError(f"Provider {provider_slug} not found")
        except Exception as e:
            raise Exception(f"Failed to find or create user: {str(e)}")
    
    @staticmethod
    def _link_social_account(user, provider, provider_user_id, email, username=None, avatar_url=None):
        """
        Link a social account to a user.
        
        Args:
            user: User instance
            provider: SocialProvider instance
            provider_user_id: Provider's user ID
            email: Email from provider
            username: Username from provider (optional)
            avatar_url: Avatar URL from provider (optional)
        """
        social_account, _ = SocialAccount.objects.get_or_create(
            user=user,
            provider=provider,
            provider_user_id=provider_user_id,
            defaults={
                'provider_email': email,
                'provider_username': username,
                'avatar_url': avatar_url,
            }
        )
        return social_account
    
    @staticmethod
    def complete_social_login(user, request=None):
        """
        Complete social login by creating session and generating tokens.
        
        Args:
            user: User instance
            request: HTTP request object
            
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
            device_info = SessionService._extract_device_info(request) if request else {}
            LoginHistory.objects.create(
                user=user,
                login_method='social',
                success=True,
                ip_address=device_info.get('ip'),
                user_agent=device_info.get('user_agent'),
                device=device_info.get('device'),
                browser=device_info.get('browser'),
                operating_system=device_info.get('os')
            )
            
            roles_list = list(user.roles.values_list('slug', flat=True))
            primary_role = "admin" if "admin" in roles_list or user.is_superuser else (roles_list[0] if roles_list else "user")
            user_profile = {
                'user_id': user.user_id,
                'email': user.email,
                'first_name': user.first_name or '',
                'last_name': user.last_name or '',
                'full_name': user.full_name,
                'role': primary_role,
                'roles': roles_list,
                'is_superuser': user.is_superuser,
                'status': user.status.slug if user.status else 'pending',
                'email_verified': user.email_verified,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat() if user.created_at else None,
            }
            
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
    def link_social_account(user, provider_slug, provider_user_id, provider_data):
        """
        Link an additional social account to an existing user.
        
        Args:
            user: User instance
            provider_slug: Provider slug
            provider_user_id: Provider's user ID
            provider_data: Dict with provider-specific data
            
        Returns:
            dict: Result
        """
        try:
            provider = SocialProvider.objects.get(slug=provider_slug)
            
            # Check if provider identity already exists
            if SocialAccount.objects.filter(
                provider=provider,
                provider_user_id=provider_user_id
            ).exists():
                return {
                    'success': False,
                    'error': 'This social account is already linked to another user'
                }
            
            # Check if user already has this provider linked
            if SocialAccount.objects.filter(
                user=user,
                provider=provider
            ).exists():
                return {
                    'success': False,
                    'error': 'You already have this provider linked to your account'
                }
            
            # Create social account link
            SocialAccount.objects.create(
                user=user,
                provider=provider,
                provider_user_id=provider_user_id,
                provider_email=provider_data.get('email'),
                provider_username=provider_data.get('username'),
                avatar_url=provider_data.get('avatar_url'),
                provider_metadata=provider_data.get('metadata', {})
            )
            
            return {
                'success': True,
                'message': 'Social account linked successfully'
            }
            
        except SocialProvider.DoesNotExist:
            return {
                'success': False,
                'error': 'Provider not found'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def unlink_social_account(user, provider_slug):
        """
        Unlink a social account from a user.
        
        Args:
            user: User instance
            provider_slug: Provider slug to unlink
            
        Returns:
            dict: Result
        """
        try:
            provider = SocialProvider.objects.get(slug=provider_slug)
            social_account = SocialAccount.objects.filter(
                user=user,
                provider=provider
            ).first()
            
            if not social_account:
                return {
                    'success': False,
                    'error': 'Social account not found'
                }
            
            # Check if user has password (required if unlinking only social auth method)
            if not user.has_usable_password():
                # Check if user has other social accounts
                other_social_accounts = SocialAccount.objects.filter(
                    user=user
                ).exclude(id=social_account.id).count()
                
                if other_social_accounts == 0:
                    return {
                        'success': False,
                        'error': 'Cannot unlink your only authentication method. Please set a password first.'
                    }
            
            social_account.delete()
            
            return {
                'success': True,
                'message': 'Social account unlinked successfully'
            }
            
        except SocialProvider.DoesNotExist:
            return {
                'success': False,
                'error': 'Provider not found'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def get_user_social_accounts(user):
        """
        Get all social accounts linked to a user.
        
        Args:
            user: User instance
            
        Returns:
            QuerySet: SocialAccount queryset
        """
        return SocialAccount.objects.filter(user=user).select_related('provider')