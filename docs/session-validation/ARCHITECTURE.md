# Session Validation Feature - Architecture Document

## System Architecture

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              User Interface (Next.js)                   │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │ │
│  │  │   Login      │  │   Dashboard  │  │   API Calls  │  │ │
│  │  │   Page       │  │   Pages      │  │   (RTK Query)│  │ │
│  │  └──────────────┘  └──────────────┘  └─────────────┘  │ │
│  └─────────────────────────────────────────────────────────┘ │
│                           │                                    │
│                           ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │            Session Storage (localStorage)               │ │
│  │  ┌─────────────────────────────────────────────────┐  │ │
│  │  │  • access_token                                   │  │ │
│  │  │  • refresh_token                                  │  │ │
│  │  │  • session_id (NEW)                               │  │ │
│  │  └─────────────────────────────────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────┘ │
│                           │                                    │
│                           ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              RTK Query Base Query Interceptor          │ │
│  │  ┌─────────────────────────────────────────────────┐  │ │
│  │  │  1. Check if public endpoint                       │  │ │
│  │  │  2. Get session_id from localStorage              │  │ │
│  │  │  3. Call session validation endpoint               │  │ │
│  │  │  4. If invalid: trigger auto-logout               │  │ │
│  │  │  5. If valid: proceed with request               │  │ │
│  │  └─────────────────────────────────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼ HTTP/HTTPS
┌─────────────────────────────────────────────────────────────┐
│                         Backend                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                    Django REST Framework               │ │
│  │  ┌─────────────────────────────────────────────────┐  │ │
│  │  │            API Gateway / Router                  │  │ │
│  │  └─────────────────────────────────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────┘ │
│                           │                                    │
│                           ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Session Validation Endpoint                │ │
│  │  ┌─────────────────────────────────────────────────┐  │ │
│  │  │  • Receive session_id                           │  │ │
│  │  │  • Query UserSession table                       │  │ │
│  │  │  • Check: exists, active, not revoked, not expired│  │ │
│  │  │  • Update last_activity                           │  │ │
│  │  │  • Return validation status                       │  │ │
│  │  └─────────────────────────────────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────┘ │
│                           │                                    │
│                           ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                    Database (PostgreSQL)                  │ │
│  │  ┌─────────────────────────────────────────────────┐  │ │
│  │  │              UserSession Table                     │  │ │
│  │  │  • usersession_id (PK, ULID)                     │  │ │
│  │  │  • user_id (FK)                                   │  │ │
│  │  │  • is_active                                     │  │ │
│  │  │  • is_revoked                                    │  │ │
│  │  │  • expires_at                                    │  │ │
│  │  │  • last_activity                                 │  │ │
│  │  │  • device_info                                   │  │ │
│  │  └─────────────────────────────────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow Diagrams

### Login Flow
```
User enters credentials
        ↓
Frontend POST /auth/login/
        ↓
Backend validates credentials
        ↓
Backend creates UserSession
        ↓
Backend generates JWT tokens
        ↓
Backend returns:
{
    "access": "jwt_token",
    "refresh": "refresh_token",
    "session_id": "uss_abc123...",  // NEW
    "user": {...}
}
        ↓
Frontend stores tokens in localStorage
        ↓
Frontend stores session_id in localStorage (NEW)
        ↓
Frontend redirects to dashboard
```

### API Request Flow (Normal)
```
User makes API request
        ↓
RTK Query interceptor intercepts
        ↓
Interceptor gets session_id from localStorage
        ↓
Interceptor calls POST /accounts/sessions/validate/
        ↓
Backend validates session:
  - Session exists? ✓
  - Session active? ✓
  - Session not revoked? ✓
  - Session not expired? ✓
        ↓
Backend updates last_activity
        ↓
Backend returns:
{
    "success": true,
    "data": { "is_valid": true }
}
        ↓
Interceptor allows request to proceed
        ↓
Original API request is made
        ↓
Backend processes request
        ↓
Response returned to frontend
```

### API Request Flow (Session Revoked)
```
User makes API request
        ↓
RTK Query interceptor intercepts
        ↓
Interceptor gets session_id from localStorage
        ↓
Interceptor calls POST /accounts/sessions/validate/
        ↓
Backend validates session:
  - Session exists? ✓
  - Session active? ✓
  - Session not revoked? ✗ (is_revoked = true)
        ↓
Backend returns:
{
    "success": false,
    "message": "Session has been revoked",
    "data": { "is_valid": false, "reason": "revoked" }
}
        ↓
Interceptor detects invalid session
        ↓
Interceptor calls handleAutoLogout()
        ↓
Auto-logout handler:
  - Clears localStorage (tokens + session_id)
  - Shows snackbar: "Session has been revoked"
  - Redirects to /auth/login?reason=revoked
        ↓
Request is cancelled
```

### Session Revocation Flow (Admin Action)
```
Admin navigates to User Sessions page
        ↓
Admin clicks "Revoke" on a session
        ↓
Frontend POST /accounts/usersessions/<id>/revoke/
        ↓
Backend sets is_revoked = True on UserSession
        ↓
Backend returns success
        ↓
Session list refreshes
        ↓
Affected user's next API request
        ↓
Session validation detects is_revoked = True
        ↓
User is auto-logged out
```

## Component Architecture

### Frontend Components

#### 1. Session Storage Utility
```javascript
// src/utils/sessionHandler.js
export const sessionHandler = {
    saveSessionId: (sessionId) => {
        localStorage.setItem('session_id', sessionId);
    },
    
    getSessionId: () => {
        return localStorage.getItem('session_id');
    },
    
    clearSession: () => {
        localStorage.removeItem('session_id');
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
    },
    
    isSessionActive: () => {
        return !!localStorage.getItem('session_id');
    }
};
```

#### 2. Session Validation API
```javascript
// src/services/session/sessionApi.js
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

#### 3. RTK Query Base Query with Validation
```javascript
// src/services/api/authApi.js
const baseQueryWithValidation = async (args, api, extraOptions) => {
    const sessionId = localStorage.getItem('session_id');
    
    // Public endpoints skip validation
    const publicEndpoints = ['/auth/login/', '/auth/register/', '/auth/refresh/'];
    const isPublic = publicEndpoints.some(endpoint => args.url.includes(endpoint));
    
    if (sessionId && !isPublic) {
        try {
            const validateResponse = await fetch(`${BASE_URL}/accounts/sessions/validate/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                },
                body: JSON.stringify({ session_id: sessionId }),
            });
            
            const validateData = await validateResponse.json();
            
            if (!validateData.success || !validateData.data?.is_valid) {
                handleAutoLogout(validateData.message);
                return { error: { status: 401, data: validateData } };
            }
        } catch (error) {
            // Fail-safe: proceed if validation fails
            console.error('Session validation failed:', error);
        }
    }
    
    return baseQuery(args, api, extraOptions);
};
```

#### 4. Auto-Logout Handler
```javascript
// src/utils/sessionHandler.js
export const handleAutoLogout = (reason = 'Session expired') => {
    // Clear session data
    clearSession();
    
    // Show notification
    showSnackbar(reason, 'warning', 5000);
    
    // Redirect to login
    window.location.href = `/auth/login?reason=${encodeURIComponent(reason)}`;
};
```

### Backend Components

#### 1. Session Validation View
```python
# account/views/session_validation.py
class SessionValidationView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        session_id = request.data.get('session_id')
        
        try:
            session = UserSession.objects.get(
                usersession_id=session_id,
                user=request.user
            )
            
            # Validation checks
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

#### 2. Login Flow Update
```python
# account/services/auth_service.py
def login_service(request):
    # ... authentication logic ...
    
    # Create session
    session = UserSession.objects.create(
        usersession_id=generate_ulid_with_prefix('uss'),
        user=user,
        device_info={
            'browser': get_browser_info(request),
            'os': get_os_info(request),
        },
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        expires_at=timezone.now() + timedelta(days=7)
    )
    
    # Generate tokens
    access_token = RefreshToken.for_user(user).access_token
    
    return {
        'access': str(access_token),
        'refresh': str(refresh_token),
        'session_id': session.usersession_id,  # NEW
        'user': UserSerializer(user).data
    }
```

## Database Schema

### UserSession Table
```sql
CREATE TABLE account_usersession (
    id BIGSERIAL PRIMARY KEY,
    usersession_id VARCHAR(50) UNIQUE NOT NULL,
    user_id BIGINT NOT NULL REFERENCES auth_user(id),
    device_info JSONB DEFAULT '{}',
    ip_address INET NOT NULL,
    user_agent TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_revoked BOOLEAN DEFAULT FALSE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    last_activity TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_usersession_user ON account_usersession(user_id);
CREATE INDEX idx_usersession_usersession_id ON account_usersession(usersession_id);
CREATE INDEX idx_usersession_expires_at ON account_usersession(expires_at);
CREATE INDEX idx_usersession_is_active ON account_usersession(is_active);
CREATE INDEX idx_usersession_is_revoked ON account_usersession(is_revoked);
```

## Security Architecture

### Session Binding
```
Session is bound to:
1. User ID
2. Device fingerprint (IP + User Agent)
3. Time window (expires_at)

This prevents:
- Token theft without device info
- Session hijacking
- Replay attacks
```

### Validation Flow
```
┌─────────────────────────────────────────────────────────┐
│  Session Validation Checks                             │
│  ┌─────────────────────────────────────────────────┐  │
│  │  1. Authentication (JWT valid?)                 │  │
│  │  2. Authorization (User has permission?)        │  │
│  │  3. Session Exists (In database?)               │  │
│  │  4. Session Active (Not deleted/inactive?)      │  │
│  │  5. Session Not Revoked (Admin didn't revoke?)   │  │
│  │  6. Session Not Expired (Within time window?)   │  │
│  │  7. Device Match (IP + User Agent match?)        │  │
│  └─────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Error Handling Strategy

### Frontend Error Handling
```
┌─────────────────────────────────────────────────────────┐
│  Validation Error Scenarios                           │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Scenario 1: No session_id                     │  │
│  │  Action: Skip validation, proceed               │  │
│  │  Reason: Public endpoint or new login          │  │
│  └─────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Scenario 2: Validation endpoint fails          │  │
│  │  Action: Log error, proceed with request        │  │
│  │  Reason: Fail-safe, don't block users           │  │
│  └─────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Scenario 3: Session invalid                     │  │
│  │  Action: Auto-logout, show notification          │  │
│  │  Reason: Security, force re-authentication       │  │
│  └─────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Scenario 4: Network error                       │  │
│  │  Action: Retry once, then proceed               │  │
│  │  Reason: Transient network issue                 │  │
│  └─────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Backend Error Handling
```
┌─────────────────────────────────────────────────────────┐
│  Backend Response Codes                               │
│  ┌─────────────────────────────────────────────────┐  │
│  │  200: Session valid                              │  │
│  │  401: Session invalid (revoked/expired/not found) │  │
│  │  403: Forbidden (user not authorized)           │  │
│  │  500: Server error (fail-safe)                   │  │
│  └─────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Performance Considerations

### Database Optimization
```sql
-- Indexes for fast session lookup
CREATE INDEX idx_usersession_lookup ON account_usersession(
    usersession_id, 
    user_id, 
    is_active, 
    is_revoked, 
    expires_at
);

-- Consider partitioning for large-scale deployments
-- Consider caching frequently accessed sessions
```

### Frontend Optimization
```javascript
// Validation results can be cached
let validationCache = new Map();
const CACHE_TTL = 30000; // 30 seconds

async function validateSession(sessionId) {
    const cached = validationCache.get(sessionId);
    if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
        return cached.result;
    }
    
    const result = await actualValidation(sessionId);
    validationCache.set(sessionId, { timestamp: Date.now(), result });
    return result;
}
```

## State Management

### localStorage Schema
```javascript
localStorage = {
    'access_token': 'eyJhbGciOiJIUzI1NiIs...',
    'refresh_token': 'eyJhbGciOiJIUzI1NiIs...',
    'session_id': 'uss_abc123xyz...',  // NEW
    'user_data': JSON.stringify({...})  // Optional
}
```

### Redux State (Optional)
```javascript
{
    session: {
        sessionId: 'uss_abc123...',
        isValid: true,
        lastValidated: '2026-10-01T10:00:00Z',
        expiresAt: '2026-10-08T10:00:00Z'
    }
}
```

## Monitoring & Observability

### Key Metrics
- Session validation endpoint response time (P50, P95, P99)
- Session validation failure rate
- Auto-logout frequency by reason
- Average session duration
- Concurrent sessions per user
- Database query performance on UserSession table

### Logging Strategy
```python
# Backend logging
logger.info(f"Session validation: {session_id} - valid={is_valid}, reason={reason}")
logger.warning(f"Auto-logout triggered: {session_id} - reason={reason}")
logger.error(f"Session validation failed: {session_id} - error={error}")
```

```javascript
// Frontend logging
console.warn(`Session invalid: ${sessionId} - ${reason}`);
console.error(`Session validation error: ${error}`);
```

## Scalability Considerations

### Horizontal Scaling
- Session validation is stateless (database-backed)
- Can be scaled across multiple application servers
- Use database connection pooling
- Consider read replicas for session validation queries

### Session Cleanup
- Implement cron job to clean up expired sessions
- Archive old session data for analytics
- Set TTL on session records
- Implement session limits per user

### Rate Limiting
```python
# Rate limit session validation endpoint
from rest_framework.throttling import UserRateThrottle

class SessionValidationThrottle(UserRateThrottle):
    rate = '60/minute'  # 60 validations per minute per user
```

## Alternative Architectures (Not Implemented)

### WebSocket-Based Real-Time Validation
**Pros**: Instant notification of revocation
**Cons**: Complex connection management, firewall issues, overhead
**Decision**: Not needed for admin dashboard use case

### Polling-Based Validation
**Pros**: Simple to implement
**Cons**: Constant server load, delayed detection
**Decision**: API interceptor is more efficient

### JWT-Only Validation (No Database)
**Pros**: No database overhead
**Cons**: Cannot revoke sessions immediately, requires rotation
**Decision**: Not sufficient for admin control requirements
