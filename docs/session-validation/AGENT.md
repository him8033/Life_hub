# Session Validation Feature - Development Guidelines

## Overview
This document provides guidelines for implementing session validation and revocation handling in the Life Hub application. Admins can revoke user sessions, and the frontend must detect and handle these revocations to log out affected users.

## Problem Statement
When an administrator revokes a user session through the admin dashboard, the affected user should be automatically logged out from the frontend application. Currently, there is no mechanism to detect session revocation on the frontend.

## Solution Approach
**API Interceptor Pattern**: Validate session status on every API request using RTK Query base query interceptor. This approach:
- Efficiently checks session validity only when user is active
- No polling overhead
- Instant detection on user action
- Simple to implement
- No WebSocket complexity

## Architecture

### Backend Components
- **UserSession Model**: Already exists with `is_active`, `is_revoked`, `user_id`, `device_info`
- **Session Revoke API**: Already exists at `/accounts/usersessions/<id>/revoke/`
- **Session Validation API**: New endpoint to validate current session status
- **JWT Token**: Should include session ID (jti) for identification

### Frontend Components
- **Session Storage**: Store session ID in localStorage/Redux on login
- **API Interceptor**: RTK Query baseQuery interceptor to validate session
- **Auto-Logout Handler**: Clear tokens and redirect on invalid session
- **Session Context**: Optional context for session state management

## Implementation Flow

### 1. Login Flow
```
User Logs In
    ↓
Backend creates UserSession
    ↓
JWT token includes session_id (jti)
    ↓
Frontend stores session_id in localStorage
    ↓
Frontend stores access_token in localStorage
```

### 2. API Request Flow
```
User makes API request
    ↓
RTK Query interceptor adds Authorization header
    ↓
Interceptor checks session_id from localStorage
    ↓
Calls session validation endpoint (if session_id exists)
    ↓
Backend validates session (exists, active, not revoked)
    ↓
If valid: Proceed with original request
    ↓
If invalid: Auto-logout user
```

### 3. Session Revocation Flow
```
Admin revokes session via admin dashboard
    ↓
Backend sets is_revoked = True on UserSession
    ↓
Next API request from affected user
    ↓
Session validation endpoint returns invalid
    ↓
Frontend auto-logs out user
    ↓
Redirect to login with notification
```

## API Specifications

### Session Validation Endpoint
**Endpoint**: `POST /api/v1/accounts/sessions/validate/`

**Request Body**:
```json
{
    "session_id": "uss_abc123..."
}
```

**Response (Valid)**:
```json
{
    "success": true,
    "message": "Session is valid",
    "data": {
        "is_valid": true,
        "session_id": "uss_abc123...",
        "user_id": "usr_xyz...",
        "expires_at": "2026-10-01T18:00:00Z"
    }
}
```

**Response (Invalid)**:
```json
{
    "success": false,
    "message": "Session has been revoked",
    "data": {
        "is_valid": false,
        "reason": "revoked" // or "expired", "not_found"
    }
}
```

### Error Response
```json
{
    "success": false,
    "statusCode": 401,
    "message": "Session invalid",
    "data": null,
    "errors": null
}
```

## Frontend Implementation

### Directory Structure
```
Life_hub_frontend/src/
├── services/
│   └── session/
│       ├── sessionApi.js          # Session validation API
│       └── index.js
├── context/
│   └── SessionContext.jsx        # Session state context (optional)
├── hooks/
│   └── useSessionValidation.js   # Custom hook for session validation
├── utils/
│   └── sessionHandler.js         # Session storage and utility functions
└── middleware/
    └── sessionInterceptor.js     # RTK Query interceptor (optional)
```

### Key Components

#### 1. Session Storage Utility (`utils/sessionHandler.js`)
```javascript
export const saveSessionId = (sessionId) => {
    localStorage.setItem('session_id', sessionId);
};

export const getSessionId = () => {
    return localStorage.getItem('session_id');
};

export const clearSession = () => {
    localStorage.removeItem('session_id');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
};

export const isSessionActive = () => {
    return !!getSessionId();
};
```

#### 2. Session Validation API (`services/session/sessionApi.js`)
```javascript
import { api } from '@/services/api/authApi';

export const sessionApi = api.injectEndpoints({
    endpoints: (builder) => ({
        validateSession: builder.mutation({
            query: (session_id) => ({
                url: '/accounts/sessions/validate/',
                method: 'POST',
                body: { session_id },
            }),
        }),
    }),
});

export const { useValidateSessionMutation } = sessionApi;
```

#### 3. RTK Query Base Query with Session Validation
Add session validation to the existing baseQuery in `authApi.js`:
```javascript
const baseQueryWithSessionValidation = async (args, api, extraOptions) => {
    const sessionId = localStorage.getItem('session_id');
    
    // Skip validation for public endpoints
    const publicEndpoints = ['/auth/login/', '/auth/register/', '/auth/refresh/'];
    const isPublic = publicEndpoints.some(endpoint => args.url.includes(endpoint));
    
    if (sessionId && !isPublic) {
        try {
            const validateResult = await fetch(`${BASE_URL}/accounts/sessions/validate/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                },
                body: JSON.stringify({ session_id: sessionId }),
            });
            
            const validateData = await validateResult.json();
            
            if (!validateData.success || !validateData.data?.is_valid) {
                // Session invalid - trigger logout
                handleAutoLogout(validateData.message);
                return { error: { status: 401, data: validateData } };
            }
        } catch (error) {
            // If validation fails, proceed with request (fail-safe)
            console.error('Session validation failed:', error);
        }
    }
    
    // Proceed with original request
    return baseQuery(args, api, extraOptions);
};
```

#### 4. Auto-Logout Handler
```javascript
export const handleAutoLogout = (reason = 'Session expired') => {
    clearSession();
    
    // Show notification
    showSnackbar(reason, 'warning', 5000);
    
    // Redirect to login
    window.location.href = '/auth/login?reason=' + encodeURIComponent(reason);
};
```

## Backend Implementation Notes

### UserSession Model (Already Exists)
```python
class UserSession(models.Model):
    id = models.BigAutoField(primary_key=True)
    usersession_id = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    device_info = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    is_active = models.BooleanField(default=True)
    is_revoked = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    last_activity = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

### Session Validation View (New)
```python
class SessionValidationView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        session_id = request.data.get('session_id')
        
        try:
            session = UserSession.objects.get(
                usersession_id=session_id,
                user=request.user
            )
            
            if session.is_revoked:
                return Response({
                    'success': False,
                    'message': 'Session has been revoked',
                    'data': {'is_valid': False, 'reason': 'revoked'}
                }, status=401)
            
            if not session.is_active:
                return Response({
                    'success': False,
                    'message': 'Session is inactive',
                    'data': {'is_valid': False, 'reason': 'inactive'}
                }, status=401)
            
            if session.expires_at < timezone.now():
                return Response({
                    'success': False,
                    'message': 'Session has expired',
                    'data': {'is_valid': False, 'reason': 'expired'}
                }, status=401)
            
            # Update last activity
            session.last_activity = timezone.now()
            session.save()
            
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
            return Response({
                'success': False,
                'message': 'Session not found',
                'data': {'is_valid': False, 'reason': 'not_found'}
            }, status=401)
```

### Login Flow Update
Update the login view/serializer to include session_id in the response:
```python
# After successful login
session = UserSession.objects.create(
    usersession_id=generate_ulid_with_prefix('uss'),
    user=user,
    device_info=device_info,
    ip_address=get_client_ip(request),
    user_agent=request.META.get('HTTP_USER_AGENT', ''),
    expires_at=timezone.now() + timedelta(days=7)
)

return Response({
    'access': str(access_token),
    'refresh': str(refresh_token),
    'session_id': session.usersession_id,  # NEW
    'user': UserSerializer(user).data
})
```

## Security Considerations

1. **Session ID in JWT**: Include session_id as a custom claim in JWT token for additional validation
2. **Session Binding**: Bind session to device fingerprint (IP + User Agent) to prevent token theft
3. **Rate Limiting**: Rate limit session validation endpoint to prevent abuse
4. **CORS**: Ensure proper CORS configuration for session validation endpoint
5. **HTTPS**: Session validation must use HTTPS in production

## Testing Strategy

### Backend Tests
- Test session validation with valid session
- Test session validation with revoked session
- Test session validation with expired session
- Test session validation with non-existent session
- Test session validation without authentication

### Frontend Tests
- Test auto-logout on session revocation
- Test auto-logout on session expiration
- Test that public endpoints don't trigger validation
- Test that validation errors don't block requests (fail-safe)
- Test localStorage management

## Verification Commands

### Backend
```bash
# Run account app tests
python manage.py test account

# Check models
python manage.py check

# Run migrations
python manage.py makemigrations account
python manage.py migrate account
```

### Frontend
```bash
# Run linting
npm run lint

# Run type checking
npm run type-check

# Build
npm run build
```

## Deployment Checklist

- [ ] Backend session validation endpoint created
- [ ] Login response includes session_id
- [ ] Frontend session storage utility created
- [ ] Frontend session validation API created
- [ ] RTK Query baseQuery updated with validation
- [ ] Auto-logout handler implemented
- [ ] Login page updated to handle session_id
- [ ] Logout function updated to clear session_id
- [ ] Test session revocation flow end-to-end
- [ ] Test session expiration flow end-to-end
- [ ] Test fail-safe behavior (validation failure)
- [ ] Update documentation

## Maintenance Notes

### Adding New Public Endpoints
Add new public endpoints to the `publicEndpoints` array in the baseQuery interceptor to skip session validation.

### Monitoring
Monitor session validation endpoint for:
- High error rates
- Performance issues
- Failed validation attempts

### Troubleshooting
- **Users logged out unexpectedly**: Check session validation logs
- **Session validation blocking requests**: Verify public endpoints list
- **Session not being validated**: Check localStorage for session_id

## Future Enhancements

1. **WebSocket Integration**: Add real-time session revocation notifications
2. **Session Analytics**: Track session duration, device usage patterns
3. **Concurrent Session Limits**: Limit number of active sessions per user
4. **Suspicious Activity Detection**: Flag unusual session patterns
5. **Session Analytics Dashboard**: Admin view of active sessions
