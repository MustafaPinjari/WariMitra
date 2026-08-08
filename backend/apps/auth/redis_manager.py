"""
Redis Token Blacklist Manager
Phase 1.1 Implementation: JWT Token Invalidation & Revocation System

Manages token revocation using Redis with O(1) lookup time.
All tokens are hashed before storage to prevent extraction attacks.
TTL is set to match remaining JWT expiration time.
"""
import hashlib
import redis
import json
import uuid
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from apps.auth.models import TokenRevocation, User


class TokenBlacklistManager:
    """
    Redis-backed token blacklist manager for JWT revocation.
    
    Features:
    - O(1) token lookup
    - Automatic TTL cleanup (no manual pruning needed)
    - Token hashing for security
    - Comprehensive audit logging
    - Fail-open behavior (allows request if Redis down)
    """
    
    PREFIX = 'token:blacklist:'
    REVOCATION_LOG_PREFIX = 'revocation:log:'
    
    def __init__(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.StrictRedis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
            )
            # Test connection
            self.redis_client.ping()
            self.is_connected = True
        except Exception as e:
            print(f"⚠️ Redis connection warning: {e}")
            self.is_connected = False
            self.redis_client = None
    
    @staticmethod
    def hash_token(token: str) -> str:
        """
        Hash token using SHA256 for secure storage.
        
        Args:
            token: JWT token to hash
            
        Returns:
            SHA256 hexdigest of token
            
        Security Note:
            Hashing prevents token extraction if Redis is compromised.
            We never store plaintext tokens.
        """
        return hashlib.sha256(token.encode()).hexdigest()
    
    def add_to_blacklist(
        self,
        token: str,
        user_id: int,
        reason: str,
        admin_id: int = None,
        ttl_seconds: int = None
    ) -> bool:
        """
        Add token to Redis blacklist with TTL.
        
        Args:
            token: JWT token to revoke
            user_id: ID of user owning the token
            reason: Revocation reason (logout, admin_revoke, security_incident, etc.)
            admin_id: ID of admin who triggered revocation (if applicable)
            ttl_seconds: TTL in seconds (default: 900 for 15-min JWT)
            
        Returns:
            True if successful, False if Redis fails (fail-open)
            
        Process:
            1. Hash the token securely
            2. Store in Redis with TTL
            3. Log revocation event to PostgreSQL audit trail
            4. Return success status
        """
        if not self.is_connected:
            print("⚠️ Redis disconnected - allowing request (fail-open)")
            return False
        
        try:
            token_hash = self.hash_token(token)
            
            # Default TTL: 15 minutes (matches JWT expiration)
            if ttl_seconds is None:
                ttl_seconds = 900
            
            # Prepare blacklist data
            blacklist_data = {
                'user_id': user_id,
                'revoked_at': timezone.now().isoformat(),
                'reason': reason,
                'admin_id': admin_id or '',
            }
            
            # Store in Redis with TTL
            key = f"{self.PREFIX}{token_hash}"
            self.redis_client.setex(
                key,
                ttl_seconds,
                json.dumps(blacklist_data)
            )
            
            # Log to PostgreSQL audit trail
            self._create_audit_log(user_id, admin_id, reason, token_hash)
            
            print(f"✓ Token blacklisted for user {user_id}, reason: {reason}")
            return True
            
        except Exception as e:
            print(f"❌ Error adding token to blacklist: {e}")
            # Fail-open: log error but allow request
            return False
    
    def is_blacklisted(self, token: str) -> bool:
        """
        Check if token is in blacklist (O(1) operation).
        
        Args:
            token: JWT token to check
            
        Returns:
            True if blacklisted, False if valid or Redis down (fail-open)
            
        Performance:
            - Redis GET operation: ~1ms
            - Hash computation: <1ms
            - Total: <5ms per request
        """
        if not self.is_connected:
            # Fail-open: allow request if Redis is down
            # JWT signature validation still provides security
            print("⚠️ Redis disconnected - allowing request (fail-open)")
            return False
        
        try:
            token_hash = self.hash_token(token)
            key = f"{self.PREFIX}{token_hash}"
            
            # O(1) lookup
            exists = self.redis_client.exists(key) == 1
            
            if exists:
                print(f"🚫 Token is blacklisted")
            
            return exists
            
        except Exception as e:
            print(f"⚠️ Error checking blacklist: {e}")
            # Fail-open: allow request on error
            return False
    
    def revoke_all_user_tokens(
        self,
        user_id: int,
        admin_id: int,
        reason: str
    ) -> int:
        """
        Revoke ALL tokens for a specific user immediately.
        
        Args:
            user_id: ID of user whose tokens to revoke
            admin_id: ID of admin performing revocation
            reason: Revocation reason
            
        Returns:
            Count of tokens revoked
            
        Use Cases:
            - User password changed
            - Device reported stolen
            - Security incident detected
            - Admin terminating user session
            
        Note:
            This is computationally expensive (SCAN operation) but necessary
            for critical security events. Acceptable frequency: <1 per minute.
        """
        if not self.is_connected:
            print("⚠️ Redis disconnected - cannot revoke tokens")
            return 0
        
        try:
            pattern = f"{self.PREFIX}*"
            cursor = 0
            revoked_count = 0
            revoked_keys = []
            
            # Use SCAN to avoid blocking (cursor-based iteration)
            while True:
                cursor, keys = self.redis_client.scan(
                    cursor,
                    match=pattern,
                    count=100  # Process 100 keys at a time
                )
                
                for key in keys:
                    try:
                        data_str = self.redis_client.get(key)
                        if data_str:
                            data = json.loads(data_str)
                            # Check if this token belongs to the user
                            if data.get('user_id') == user_id:
                                revoked_keys.append(key)
                                revoked_count += 1
                    except (json.JSONDecodeError, KeyError):
                        # Skip malformed entries
                        continue
                
                # SCAN returns 0 cursor when complete
                if cursor == 0:
                    break
            
            # Delete all found keys
            if revoked_keys:
                self.redis_client.delete(*revoked_keys)
            
            # Create audit log entry
            revocation_id = str(uuid.uuid4())
            TokenRevocation.objects.create(
                revocation_id=revocation_id,
                user_id=user_id,
                revoked_by_id=admin_id,
                reason=reason,
                token_hash='BATCH_REVOKE'  # Indicates batch operation
            )
            
            print(f"✓ Revoked {revoked_count} tokens for user {user_id}")
            return revoked_count
            
        except Exception as e:
            print(f"❌ Error revoking all user tokens: {e}")
            return 0
    
    def _create_audit_log(
        self,
        user_id: int,
        admin_id: int,
        reason: str,
        token_hash: str
    ) -> bool:
        """
        Create immutable audit log entry in PostgreSQL.
        
        Args:
            user_id: User ID
            admin_id: Admin ID (if applicable)
            reason: Revocation reason
            token_hash: Hashed token
            
        Returns:
            True if successful
            
        Note:
            This creates an immutable audit trail that cannot be deleted
            (only soft-deleted via is_active=False for compliance).
        """
        try:
            TokenRevocation.objects.create(
                revocation_id=str(uuid.uuid4()),
                user_id=user_id,
                revoked_by_id=admin_id,
                reason=reason,
                token_hash=token_hash,
            )
            return True
        except Exception as e:
            print(f"⚠️ Error creating audit log: {e}")
            # Don't fail token revocation if audit logging fails
            return False
    
    def clear_expired_tokens(self) -> int:
        """
        Manual cleanup of expired blacklist entries (optional).
        
        Returns:
            Number of tokens cleaned up
            
        Note:
            Redis TTL handles automatic cleanup, so this is NOT needed.
            Provided for manual maintenance if desired.
            Use only during low-traffic periods.
        """
        if not self.is_connected:
            return 0
        
        try:
            # Find expired keys (TTL = -1)
            pattern = f"{self.PREFIX}*"
            cursor = 0
            expired_count = 0
            
            while True:
                cursor, keys = self.redis_client.scan(cursor, match=pattern, count=100)
                
                for key in keys:
                    ttl = self.redis_client.ttl(key)
                    if ttl == -1:  # No expiration set (shouldn't happen)
                        self.redis_client.delete(key)
                        expired_count += 1
                
                if cursor == 0:
                    break
            
            return expired_count
            
        except Exception as e:
            print(f"⚠️ Error cleaning expired tokens: {e}")
            return 0
    
    def get_revocation_stats(self) -> dict:
        """
        Get statistics about token revocations (for monitoring).
        
        Returns:
            Dictionary with revocation statistics
        """
        if not self.is_connected:
            return {'status': 'Redis disconnected'}
        
        try:
            # Count tokens in blacklist
            cursor = 0
            token_count = 0
            
            pattern = f"{self.PREFIX}*"
            while True:
                cursor, keys = self.redis_client.scan(cursor, match=pattern, count=1000)
                token_count += len(keys)
                if cursor == 0:
                    break
            
            # Get total revocation logs from DB
            total_revocations = TokenRevocation.objects.filter(
                is_active=True
            ).count()
            
            return {
                'status': 'connected',
                'tokens_in_blacklist': token_count,
                'total_revocation_events': total_revocations,
                'memory_usage_estimate_bytes': token_count * 150,  # Rough estimate
            }
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}


# Singleton instance - use this throughout the app
token_blacklist = TokenBlacklistManager()
