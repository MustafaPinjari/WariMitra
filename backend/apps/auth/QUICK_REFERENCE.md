# Phase 1.1: JWT Token Invalidation - Quick Reference

## For Developers

### Quick Start
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Run tests
pytest apps/auth/tests/ -v

# Start server
python manage.py runserver
```

### API Endpoints

#### 1. Logout
```bash
POST /api/v1/auth/logout/
Authorization: Bearer <token>

# Response
{
  "message": "Token revoked successfully",
  "revocation_id": "uuid"
}
```

#### 2. Admin Revoke
```bash
POST /api/v1/admin/users/{user_id}/revoke-tokens/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "reason": "security_incident"
}

# Response
{
  "message": "All tokens revoked for user ...",
  "revoked_count": 5,
  "revocation_id": "uuid"
}
```

#### 3. View Audit Logs
```bash
GET /api/v1/auth/revocations/
Authorization: Bearer <admin_token>

# Query params: ?user=1&reason=logout&page=1
```

### Code Examples

#### Check if Token is Blacklisted
```python
from apps.auth.redis_manager import token_blacklist

# Check if token is blacklisted
is_blacklisted = token_blacklist.is_blacklisted(token)
if is_blacklisted:
    # Token has been revoked
    return 401
```

#### Revoke a Token
```python
from apps.auth.redis_manager import token_blacklist

# Add token to blacklist
result = token_blacklist.add_to_blacklist(
    token=token_string,
    user_id=user.id,
    reason='logout',
    ttl_seconds=900
)
```

#### Query Audit Logs
```python
from apps.auth.models import TokenRevocation

# All logout events
logouts = TokenRevocation.objects.filter(reason='logout')

# All admin revocations
admin_revokes = TokenRevocation.objects.filter(reason='admin_revoke')

# By admin user
by_admin = TokenRevocation.objects.filter(revoked_by_id=admin_user.id)

# Recent events
recent = TokenRevocation.objects.filter(reason='security_incident')[:10]
```

### Testing

#### Run All Tests
```bash
pytest apps/auth/tests/ -v
```

#### Run Specific Test
```bash
pytest apps/auth/tests/test_views.py::TestLogoutView::test_logout_success -v
```

#### With Coverage
```bash
pytest apps/auth/tests/ --cov=apps.auth --cov-report=html
```

#### Debug Tests
```bash
pytest apps/auth/tests/test_views.py -s -vv
```

### Common Tasks

#### Clear Redis Blacklist
```python
python manage.py shell
>>> from apps.auth.redis_manager import token_blacklist
>>> token_blacklist.clear_blacklist()
```

#### Check Redis Connection
```python
python manage.py shell
>>> from apps.auth.redis_manager import token_blacklist
>>> token_blacklist.is_available()
True
```

#### Export Audit Logs
```bash
python manage.py shell
>>> from apps.auth.models import TokenRevocation
>>> import json
>>> revocations = TokenRevocation.objects.all()
>>> for r in revocations:
...     print(json.dumps({
...         'user': r.user.username,
...         'reason': r.reason,
...         'timestamp': r.created_at.isoformat(),
...     }))
```

### Troubleshooting

#### Token Still Works After Revocation
**Cause:** Redis blacklist not available  
**Fix:** Check Redis is running: `docker-compose ps | grep redis`

#### Logout Returns 500 Error
**Cause:** Redis connection issue  
**Fix:** Check Redis logs: `docker-compose logs redis`

#### Admin Revoke Forbidden
**Cause:** User is not admin  
**Fix:** Make user admin: `python manage.py shell`
```python
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.get(username='admin')
>>> user.is_staff = True
>>> user.save()
```

#### Tests Failing
**Cause:** Django not set up  
**Fix:** Install dependencies: `pip install -r requirements.txt`

### Configuration

#### Environment Variables
```bash
# .env file
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=your_password  # Optional
```

#### Settings
```python
# backend/config/settings/base.py

# Already configured:
AUTH_USER_MODEL = 'auth.CustomUser'
MIDDLEWARE = [..., 'apps.auth.middleware.BlacklistCheckMiddleware']
REDIS_HOST = config('REDIS_HOST', default='localhost')
REDIS_PORT = config('REDIS_PORT', default=6379, cast=int)
```

### Performance

#### Check Blacklist Lookup Time
```python
import time
from apps.auth.redis_manager import token_blacklist

start = time.time()
result = token_blacklist.is_blacklisted(token)
elapsed = (time.time() - start) * 1000
print(f"Lookup: {elapsed:.2f}ms")  # Should be <5ms
```

#### Check Database Query Time
```python
import time
from apps.auth.models import TokenRevocation

start = time.time()
list(TokenRevocation.objects.filter(reason='logout')[:10])
elapsed = (time.time() - start) * 1000
print(f"Query: {elapsed:.2f}ms")  # Should be <10ms
```

### Files to Know

| File | Purpose |
|------|---------|
| `middleware.py` | Blacklist check on every request |
| `views.py` | Logout and admin revoke endpoints |
| `serializers.py` | Request/response validation |
| `models.py` | TokenRevocation audit model |
| `urls.py` | Endpoint routing |
| `redis_manager.py` | Redis blacklist operations |
| `tests/` | All test cases |

### Key Concepts

#### Token Revocation
Marks a JWT token as invalid immediately, preventing its use even before natural expiration.

#### Redis Blacklist
Fast, in-memory storage of revoked token hashes with automatic cleanup when token expires.

#### Audit Log
Immutable database record of every revocation event for compliance and debugging.

#### Backward Compatible
Existing tokens continue to work, new code doesn't break old clients.

### What's Next?

**Phase 1.2:** DDoS Protection (rate limiting)  
**Phase 1.3:** Data Encryption (field-level)  
**Phase 1.4:** Object-Level RBAC  

See `IMPLEMENTATION_GUIDE.md` for full roadmap.

---

**Need Help?** Check `PHASE_1_1_IMPLEMENTATION.md` for detailed documentation.

