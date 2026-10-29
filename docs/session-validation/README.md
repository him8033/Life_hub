# Session Validation Feature

## Overview
This feature enables administrators to revoke user sessions through the admin dashboard, with automatic logout of affected users on the frontend. The implementation uses an API interceptor pattern to validate session status on every API request.

## Documentation
- **[AGENT.md](./AGENT.md)** - Development guidelines and implementation details
- **[PLAN.md](./PLAN.md)** - Step-by-step implementation plan
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - System architecture and design decisions

## Quick Start

### For Developers
1. Read [AGENT.md](./AGENT.md) to understand the development guidelines
2. Review [PLAN.md](./PLAN.md) to understand the implementation phases
3. Study [ARCHITECTURE.md](./ARCHITECTURE.md) to understand the system design
4. Follow the implementation plan in order

### For Implementation
```bash
# Navigate to docs directory
cd docs/session-validation

# Read documentation in order
1. Read AGENT.md
2. Read PLAN.md
3. Read ARCHITECTURE.md
4. Begin implementation following PLAN.md
```

## Implementation Status
- [ ] Phase 1: Backend Preparation
- [ ] Phase 2: Frontend Utilities
- [ ] Phase 3: Frontend Integration
- [ ] Phase 4: Testing & Verification
- [ ] Phase 5: Documentation & Cleanup

## Key Features
- ✅ Session validation on every API request
- ✅ Automatic logout on session revocation
- ✅ Automatic logout on session expiration
- ✅ Session ID storage in localStorage
- ✅ Fail-safe behavior (validation failure doesn't block requests)
- ✅ Public endpoints skip validation
- ✅ Admin control over user sessions

## Technology Stack
- **Backend**: Django REST Framework, PostgreSQL
- **Frontend**: Next.js, RTK Query, localStorage
- **Authentication**: JWT (djangorestframework-simplejwt)

## API Endpoints

### Backend
- `POST /api/v1/accounts/sessions/validate/` - Validate session status
- `POST /api/v1/accounts/usersessions/<id>/revoke/` - Revoke session (already exists)

### Frontend
- Session validation via RTK Query baseQuery interceptor
- Auto-logout handler utility

## File Structure

### Backend
```
Life_hub/account/
├── views/
│   └── session_validation.py      # NEW - Session validation view
├── urls.py                       # UPDATE - Add validation endpoint
└── services/
    └── auth_service.py           # UPDATE - Add session_id to login response
```

### Frontend
```
Life_hub_frontend/src/
├── utils/
│   └── sessionHandler.js         # NEW - Session storage utilities
├── services/
│   └── session/
│       ├── sessionApi.js          # NEW - Session validation API
│       └── index.js
└── services/api/
    └── authApi.js                # UPDATE - Add validation to baseQuery
```

## Security Features
- Session binding to device fingerprint
- Session expiration handling
- Revocation detection
- Rate limiting on validation endpoint
- HTTPS required in production

## Testing
- Backend unit tests for session validation
- Frontend tests for auto-logout behavior
- End-to-end tests for session revocation flow
- Edge case testing (no session_id, validation failure, etc.)

## Monitoring
- Session validation endpoint response time
- Session validation failure rate
- Auto-logout frequency
- Database query performance on UserSession table

## Deployment Checklist
See [PLAN.md](./PLAN.md) for complete deployment checklist.

## Troubleshooting
See [AGENT.md](./AGENT.md) for troubleshooting section.

## Future Enhancements
- WebSocket integration for real-time notifications
- Session analytics dashboard
- Concurrent session limits
- Suspicious activity detection

## Contact
For questions or issues, refer to the main project documentation or contact the development team.
