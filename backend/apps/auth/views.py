"""
Authentication views for WariMitra
Phase 1.1 Implementation: JWT Token Invalidation & Revocation System
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from .serializers import CustomTokenObtainPairSerializer, LogoutSerializer, RevokeTokensSerializer
from .models import User, TokenRevocation
from .redis_manager import token_blacklist
import logging

logger = logging.getLogger(__name__)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom token obtain view with user data.
    
    Returns JWT access and refresh tokens along with user information.
    """
    serializer_class = CustomTokenObtainPairSerializer


class LogoutView(APIView):
    """
    User logout endpoint.
    
    Endpoint: POST /api/v1/auth/logout/
    Permission: IsAuthenticated
    
    Process:
        1. Extract JWT token from Authorization header
        2. Hash and add token to Redis blacklist
        3. Create audit log entry in PostgreSQL
        4. Return 200 OK
        
    Response:
        {
            "message": "Logged out successfully",
            "timestamp": "2024-01-30T10:30:00Z"
        }
    
    Errors:
        - 400: No token provided
        - 401: Unauthorized
        - 500: Server error
    """
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer
    
    def post(self, request):
        """
        Process user logout and revoke current token.
        
        Args:
            request: HTTP request with JWT token in Authorization header
            
        Returns:
            Response with status 200 on success
        """
        try:
            # Extract token from Authorization header
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            
            if not auth_header.startswith('Bearer '):
                logger.warning(f"Logout attempt without Bearer token from {request.META.get('REMOTE_ADDR')}")
                return Response(
                    {'error': 'No token provided'},
                    status=400
                )
            
            token = auth_header[7:]  # Remove 'Bearer ' prefix
            
            # Validate token format (should be present and non-empty)
            if not token or len(token) < 50:  # JWT tokens are typically 150+ chars
                logger.warning(f"Logout attempt with malformed token from {request.META.get('REMOTE_ADDR')}")
                return Response(
                    {'error': 'Invalid token format'},
                    status=400
                )
            
            # Add token to Redis blacklist with TTL
            # Default TTL: 900 seconds (15 minutes) matching JWT expiration
            success = token_blacklist.add_to_blacklist(
                token=token,
                user_id=request.user.id,
                reason='logout',
                admin_id=None,
                ttl_seconds=900  # Match JWT_ACCESS_TOKEN_LIFETIME
            )
            
            if not success:
                logger.error(f"Failed to blacklist token for user {request.user.id}")
                # Don't fail logout even if Redis is down (fail-open)
                # User should still be logged out on client side
            
            logger.info(f"User {request.user.id} ({request.user.username}) logged out successfully")
            
            return Response(
                {
                    'message': 'Logged out successfully',
                    'detail': 'Your token has been revoked. Please log in again.',
                },
                status=200
            )
            
        except Exception as e:
            logger.error(f"Error during logout: {str(e)}", exc_info=True)
            return Response(
                {'error': 'An error occurred during logout'},
                status=500
            )


class RevokeAllUserTokensView(APIView):
    """
    Admin endpoint to revoke ALL tokens for a specific user.
    
    Endpoint: POST /api/v1/admin/users/{user_id}/revoke-tokens/
    Permission: IsAuthenticated + IsAdminUser
    
    Use Cases:
        - User password changed
        - Device reported stolen
        - Security incident detected
        - Terminating user session
        - User fired/suspended
    
    Request Body:
        {
            "reason": "security_incident" | "admin_action" | "password_reset" | "device_lost"
        }
    
    Response:
        {
            "message": "All tokens revoked successfully",
            "user_id": 123,
            "revoked_count": 5,
            "revocation_id": "12345678-1234-1234-1234-123456789012"
        }
    
    Errors:
        - 404: User not found
        - 403: Insufficient permissions
        - 500: Server error
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = RevokeTokensSerializer
    
    def post(self, request, user_id):
        """
        Revoke all tokens for a specific user.
        
        Args:
            request: HTTP request with admin JWT token
            user_id: ID of user whose tokens to revoke
            
        Returns:
            Response with revocation status
        """
        try:
            # Verify target user exists
            try:
                target_user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                logger.warning(
                    f"Admin {request.user.id} attempted to revoke tokens for non-existent user {user_id}"
                )
                return Response(
                    {'error': 'User not found', 'user_id': user_id},
                    status=404
                )
            
            # Get revocation reason from request
            reason = request.data.get('reason', 'admin_action')
            
            # Validate reason is one of allowed choices
            allowed_reasons = ['logout', 'admin_revoke', 'password_reset', 'security_incident', 'device_lost']
            if reason not in allowed_reasons:
                logger.warning(f"Invalid revocation reason: {reason}")
                return Response(
                    {
                        'error': 'Invalid revocation reason',
                        'allowed_reasons': allowed_reasons
                    },
                    status=400
                )
            
            # Revoke all tokens in Redis for this user
            revoked_count = token_blacklist.revoke_all_user_tokens(
                user_id=user_id,
                admin_id=request.user.id,
                reason=reason
            )
            
            logger.info(
                f"Admin {request.user.id} ({request.user.username}) revoked {revoked_count} "
                f"tokens for user {user_id} ({target_user.username}). Reason: {reason}"
            )
            
            return Response(
                {
                    'message': 'All tokens revoked successfully',
                    'user_id': user_id,
                    'username': target_user.username,
                    'revoked_count': revoked_count,
                    'reason': reason,
                },
                status=200
            )
            
        except Exception as e:
            logger.error(
                f"Error revoking tokens for user {user_id}: {str(e)}",
                exc_info=True
            )
            return Response(
                {'error': 'An error occurred while revoking tokens'},
                status=500
            )
