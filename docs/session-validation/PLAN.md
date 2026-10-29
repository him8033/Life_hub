# Session Validation Feature - Implementation Plan

## Overview
This document outlines the step-by-step implementation plan for adding session validation and revocation handling to the Life Hub application.

## Prerequisites
- Backend UserSession model already exists
- Backend session revoke API already exists
- Frontend auth system with JWT tokens already exists
- RTK Query is already configured

## Implementation Phases

### Phase 1: Backend Preparation
**Estimated Time**: 30 minutes

#### Step 1.1: Create Session Validation Endpoint
- **File**: `account/views/session_validation.py` (new)
- **Task**: Create `SessionValidationView` class
- **Details**:
  - Accept POST request with `session_id`
  - Validate session exists, is active, not revoked, not expired
  - Update `last_activity` timestamp
  - Return session validity status

#### Step 1.2: Add URL Routing
- **File**: `account/urls.py`
- **Task**: Add session validation endpoint
- **Route**: `POST /api/v1/accounts/sessions/validate/`

#### Step 1.3: Update Login Response
- **File**: `account/services/auth_service.py` or login view
- **Task**: Include `session_id` in login response
- **Details**:
  - Create UserSession after successful login
  - Return `session_id` in response along with tokens
  - Store device info (IP, User Agent)

#### Step 1.4: Update Logout Handler
- **File**: `account/services/auth_service.py` or logout view
- **Task**: Invalidate session on logout
- **Details**:
  - Set `is_active = False` on UserSession
  - Clear session from database

#### Step 1.5: Backend Testing
- Test session validation endpoint
- Test login response includes session_id
- Test logout invalidates session
- Test revoked session returns invalid

---

### Phase 2: Frontend Utilities
**Estimated Time**: 20 minutes

#### Step 2.1: Create Session Storage Utility
- **File**: `src/utils/sessionHandler.js` (new)
- **Task**: Create session storage functions
- **Functions**:
  - `saveSessionId(sessionId)` - Save to localStorage
  - `getSessionId()` - Retrieve from localStorage
  - `clearSession()` - Clear all session data
  - `isSessionActive()` - Check if session exists

#### Step 2.2: Create Auto-Logout Handler
- **File**: `src/utils/sessionHandler.js`
- **Task**: Create auto-logout function
- **Function**: `handleAutoLogout(reason)`
- **Details**:
  - Clear session data
  - Show snackbar notification
  - Redirect to login page with reason

#### Step 2.3: Create Session Validation API
- **File**: `src/services/session/sessionApi.js` (new)
- **Task**: Create RTK Query API for session validation
- **Endpoints**:
  - `validateSession` - POST mutation to validate session

#### Step 2.4: Update Auth API Base Configuration
- **File**: `src/services/api/authApi.js`
- **Task**: Add session validation to baseQuery
- **Details**:
  - Add session validation logic to baseQuery
  - Skip validation for public endpoints
  - Trigger auto-logout on invalid session
  - Fail-safe: proceed if validation fails

---

### Phase 3: Frontend Integration
**Estimated Time**: 30 minutes

#### Step 3.1: Update Login Page
- **File**: `src/app/(root)/auth/login/page.jsx`
- **Task**: Store session_id after successful login
- **Details**:
  - Extract `session_id` from login response
  - Call `saveSessionId(sessionId)`
  - Store in localStorage

#### Step 3.2: Update Logout Function
- **File**: `src/utils/auth.js` or similar
- **Task**: Clear session_id on logout
- **Details**:
  - Call `clearSession()` instead of just clearing tokens
  - Ensure all session data is removed

#### Step 3.3: Add Session API to Redux Store
- **File**: `src/redux/store.js`
- **Task**: Add sessionApi reducer and middleware
- **Details**:
  - Import sessionApi
  - Add to reducer
  - Add to middleware

#### Step 3.4: Test Session Storage
- Test session_id is saved on login
- Test session_id is cleared on logout
- Test localStorage persistence
- Test session_id retrieval

---

### Phase 4: Testing & Verification
**Estimated Time**: 30 minutes

#### Step 4.1: Backend Testing
```bash
# Test session validation endpoint
curl -X POST http://127.0.0.1:8000/api/v1/accounts/sessions/validate/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "uss_abc123..."}'

# Test with revoked session
# Test with expired session
# Test with non-existent session
```

#### Step 4.2: Frontend Testing
- Test login stores session_id
- Test logout clears session_id
- Test API request with valid session
- Test API request with revoked session (should auto-logout)
- Test public endpoints skip validation
- Test auto-logout notification and redirect

#### Step 4.3: End-to-End Testing
1. Login as user
2. Verify session_id is stored
3. Make API request (should succeed)
4. Admin revokes session via admin dashboard
5. User makes another API request
6. Verify auto-logout happens
7. Verify redirect to login with notification

#### Step 4.4: Edge Cases
- Test with no session_id (should skip validation)
- Test with invalid session_id (should auto-logout)
- Test validation endpoint failure (should proceed with request)
- Test multiple concurrent sessions
- Test session expiration

---

### Phase 5: Documentation & Cleanup
**Estimated Time**: 15 minutes

#### Step 5.1: Update Documentation
- Update AGENTS.md with session validation notes
- Update ARCHITECTURE.md with session flow diagrams
- Update README.md with usage instructions

#### Step 5.2: Code Cleanup
- Remove console.log statements
- Add proper error handling
- Add code comments where needed
- Format code consistently

#### Step 5.3: Final Verification
- Run backend tests
- Run frontend linting
- Run frontend build
- Test complete flow one more time

---

## Deployment Checklist

### Backend
- [ ] Session validation endpoint created
- [ ] URL routing added
- [ ] Login response includes session_id
- [ ] Logout invalidates session
- [ ] Backend tests passing
- [ ] Database migrations run (if any)

### Frontend
- [ ] Session storage utility created
- [ ] Auto-logout handler created
- [ ] Session validation API created
- [ ] Auth API baseQuery updated
- [ ] Login page updated
- [ ] Logout function updated
- [ ] Redux store updated
- [ ] Frontend linting passing
- [ ] Frontend build passing

### Integration
- [ ] End-to-end testing complete
- [ ] Session revocation tested
- [ ] Session expiration tested
- [ ] Public endpoints tested
- [ ] Edge cases tested
- [ ] Documentation updated

---

## Rollback Plan

If issues arise during implementation:

### Backend Rollback
1. Remove session validation endpoint from URLs
2. Comment out session_id from login response
3. Revert logout changes
4. Restore previous login/logout behavior

### Frontend Rollback
1. Remove session validation from baseQuery
2. Remove session storage calls from login/logout
3. Remove sessionApi from Redux store
4. Delete session handler utility files

---

## Success Criteria

The implementation is successful when:
1. Login response includes session_id
2. Session_id is stored in localStorage
3. Every API request validates session (except public endpoints)
4. Revoked sessions trigger auto-logout
5. Expired sessions trigger auto-logout
6. Auto-logout shows notification and redirects to login
7. Public endpoints skip session validation
8. Validation failures don't block requests (fail-safe)
9. Backend and frontend tests pass
10. No console errors in production

---

## Time Estimates

| Phase | Estimated Time |
|-------|----------------|
| Phase 1: Backend Preparation | 30 min |
| Phase 2: Frontend Utilities | 20 min |
| Phase 3: Frontend Integration | 30 min |
| Phase 4: Testing & Verification | 30 min |
| Phase 5: Documentation & Cleanup | 15 min |
| **Total** | **~2 hours** |

---

## Risks & Mitigations

### Risk 1: Performance Impact
**Risk**: Session validation on every API request may slow down performance
**Mitigation**: 
- Use efficient database queries
- Add indexes on session_id
- Cache session validation results
- Monitor performance metrics

### Risk 2: Validation Endpoint Failure
**Risk**: If validation endpoint fails, all API requests fail
**Mitigation**: 
- Fail-safe: proceed with original request if validation fails
- Log validation failures for monitoring
- Add health check for validation endpoint

### Risk 3: Race Conditions
**Risk**: Session revoked between validation and API request
**Mitigation**: 
- Use database transactions
- Update last_activity before checking revocation
- Add retry logic for critical operations

### Risk 4: Frontend Storage Issues
**Risk**: localStorage may be cleared or unavailable
**Mitigation**: 
- Graceful degradation: skip validation if no session_id
- Provide fallback to cookie-based storage
- Handle localStorage quota exceeded errors

---

## Post-Implementation Monitoring

### Metrics to Track
- Session validation endpoint response time
- Session validation failure rate
- Auto-logout frequency
- Average session duration
- Concurrent sessions per user

### Alerts to Set Up
- High session validation failure rate (>5%)
- Slow validation response time (>500ms)
- High auto-logout rate (possible bug)
- Database query performance on session table
