"""
Token Blacklist Middleware
Phase 1.1 Implementation: JWT Token Invalidation & Revocation System

Checks every request with a JWT token against the Redis blacklist.
Runs BEFORE the view is processed, ensuring revoked tokens are rejected early.
Performance: <1ms per request (O(1) Redis lookup + hash computation).
"""
from django.http import JsonResponse
from django.utils.decorators import sync_and_async_middleware
import logging

logger = logging.getLogger(__name__)


class TokenBlacklistMiddleware:
    """
    Middleware to check JWT tokens against Redis blacklist.
    
    Placement in MIDDLEWARE:
        Should be placed AFTER AuthenticationMiddleware but BEFORE view execution.
        
    Process:
        1. Extract Authorization header
        2. If token present, check Redis blacklist
        3. If blacklisted, return 401 Unauthorized
        4. If valid or Redis down (fail-open), proceed to view
    """
    
    def __init__(self, get_response):
        """Initialize middleware with response handler"""
        self.get_response = get_response
    
    def __call__(self, request):
        """
        Process request and check token blacklist.
        
        Returns:
            401 if token is blacklisted
            Original response if token is valid or Redis unavailable
        """
        # Import here to avoid circular imports
        from .redis_manager import token_blacklist
        
        # Extract Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        # Check if Bearer token is present
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]  # Remove 'Bearer ' prefix
            
            # Check if token is blacklisted
            if token_blacklist.is_blacklisted(token):
                logger.warning(
                    f"Blocked request with blacklisted token from {request.META.get('REMOTE_ADDR')}"
                )
                return JsonResponse(
                    {
                        'error': 'Token has been revoked',
                        'detail': 'This token is no longer valid. Please log in again.',
                        'code': 'token_revoked'
                    },
                    status=401
                )
        
        # Token is valid or no token present - proceed to view
        response = self.get_response(request)
        return response


# Alternative: DRF-based authentication class (if preferred)
class TokenBlacklistAuthentication:
    """
    DRF custom authentication class to check blacklist.
    
    Can be used INSTEAD of middleware if you prefer handling in DRF layer.
    Add to REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] in settings.
    
    Usage in settings.py:
        REST_FRAMEWORK = {
            'DEFAULT_AUTHENTICATION_CLASSES': [
                'rest_framework_simplejwt.authentication.JWTAuthentication',
                'apps.auth.middleware.TokenBlacklistAuthentication',
            ],
        }
    """
    
    def authenticate(self, request):
        """Check blacklist during authentication"""
        from .redis_manager import token_blacklist
        from rest_framework.exceptions import AuthenticationFailed
        
        # Get token from request
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            
            # Check blacklist
            if token_blacklist.is_blacklisted(token):
                logger.warning(
                    f"Blocked request with blacklisted token from {request.META.get('REMOTE_ADDR')}"
                )
                raise AuthenticationFailed('Token has been revoked')
        
        return None  # Not handling this authentication, pass to next
    
    def authenticate_header(self, request):
        """DRF authentication header for WWW-Authenticate"""
        return 'Bearer'
