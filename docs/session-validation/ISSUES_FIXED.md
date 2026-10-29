# Session Validation - Issues Fixed

## Issues Found and Fixed

### Issue 1: Storage Mismatch (Critical)
**Problem:**
- `tokenService` stores `session_id` in **Cookies**
- `sessionHandler.getSessionId()` was reading from **localStorage**
- Login page was saving to **localStorage** using `saveSessionId()`

This caused the session validation to fail because:
1. Login saves session_id to localStorage
2. BaseQuery reads from localStorage (gets the value)
3. But tokenService saves to cookies (different storage)
4. Inconsistency between storage mechanisms

**Fix:**
- Updated `sessionHandler.js` to use **Cookies** instead of localStorage
- Now both `tokenService` and `sessionHandler` use the same storage (Cookies)
- Removed duplicate `saveSessionId()` call from login page (tokenService already handles it)

### Issue 2: Backend Field Name Error (Critical)
**Problem:**
- Session validation view was trying to update `session.last_activity`
- But the model field is actually `session.last_activity_at`
- This caused a database error every time session validation ran

**Fix:**
- Changed `session.last_activity` to `session.last_activity_at` in session_validation.py
- Changed update_fields from `['last_activity']` to `['last_activity_at']`

## How to Test

### Step 1: Start the Applications
```bash
# Backend
cd D:\Practical\Life_Hub\Life_hub
python manage.py runserver

# Frontend
cd D:\Practical\Life_Hub\Life_hub_frontend
npm run dev
```

### Step 2: Login as a User
1. Navigate to `http://localhost:3000/auth/login`
2. Login with valid credentials
3. Check browser console - you should see:
   ```
   Session debug utilities available:
     - debugSessionStorage()
     - testSessionValidation()
   ```

### Step 3: Debug Session Storage
Open browser console and run:
```javascript
debugSessionStorage()
```

Expected output:
```
=== Session Storage Debug ===
getSessionId(): uss_abc123...
tokenService.get().session_id: uss_abc123...
Cookies session_id: session_id=uss_abc123...
tokenService.get(): { access: "...", refresh: "...", user: {...}, session_id: "uss_abc123...", device: "..." }
============================
```

Both `getSessionId()` and `tokenService.get().session_id` should show the same value.

### Step 4: Test Session Validation
Open browser console and run:
```javascript
testSessionValidation()
```

Expected output:
```
Testing session validation...
Session ID: uss_abc123...
Base URL: http://localhost:8000
Session Validation Response: { success: true, message: "Session is valid", data: { is_valid: true, ... } }
Response Status: 200
```

### Step 5: Revoke Session
1. Login as an admin (or use the same user if they have admin access)
2. Navigate to User Sessions page: `http://localhost:3000/dashboard/account/usersessions`
3. Find the session you want to revoke
4. Click "Revoke" button
5. Confirm the revocation

### Step 6: Test Auto-Logout
1. On the revoked user's browser, make any API request (navigate to any page)
2. The user should be automatically logged out
3. Redirected to login page with message: "Session has been revoked by an administrator"

### Step 7: Verify Storage After Revocation
On the revoked user's browser console:
```javascript
debugSessionStorage()
```

Expected output:
```
=== Session Storage Debug ===
getSessionId(): null
tokenService.get().session_id: null
Cookies session_id: undefined
tokenService.get(): { access: null, refresh: null, user: null, session_id: null, device: null }
============================
```

All values should be null after logout.

## Debugging Commands

These commands are available in the browser console after loading any page:

### `debugSessionStorage()`
Shows current session storage state from both localStorage and Cookies.

### `testSessionValidation()`
Manually tests the session validation endpoint and shows the response.

## Files Modified

### Frontend
1. `src/utils/sessionHandler.js` - Changed from localStorage to Cookies
2. `src/app/(root)/auth/login/page.jsx` - Removed duplicate saveSessionId call, added debug import
3. `src/app/(root)/dashboard/account/usersessions/page.jsx` - Added debug import
4. `src/utils/sessionDebug.js` - NEW - Debug utilities for testing

### Backend
1. `account/views/session_validation.py` - Fixed field name `last_activity` → `last_activity_at`

## Common Issues and Solutions

### Issue: Session not being validated
**Check:** Run `debugSessionStorage()` in console
**Solution:** Ensure both `getSessionId()` and `tokenService.get().session_id` return the same value

### Issue: Auto-logout not triggering
**Check:** Run `testSessionValidation()` in console
**Solution:** Ensure the validation endpoint returns success: true with is_valid: true

### Issue: Database error on validation
**Check:** Backend logs for "no such field: last_activity"
**Solution:** Ensure the fix is applied (field name changed to last_activity_at)

### Issue: Login loop (user logged out immediately after login)
**Check:** If session validation is failing on valid sessions
**Solution:** Check that the session validation endpoint is working correctly with `testSessionValidation()`

## Next Steps

1. Test the fix with the steps above
2. Verify session revocation works correctly
3. Test with multiple users and sessions
4. Test with expired sessions
5. Remove debug utilities in production (optional)
