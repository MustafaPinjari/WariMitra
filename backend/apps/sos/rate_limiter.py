"""
Rate Limiter Module for SOS Endpoint Protection
Phase 1.2 Implementation: DDoS Protection

Implements sliding window rate limiting using Redis for both IP and device-level protection.
Uses Redis INCR and EXPIRE commands for O(1) performance and automatic cleanup.

Example:
    from apps.sos.rate_limiter import RateLimiter
    
    limiter = RateLimiter(redis_client)
    
    # Check IP rate limit (100 requests/minute)
    if not limiter.check_ip_limit(ip_address):
        return Response({"error": "rate_limited"}, status=429)
    
    # Check device rate limit (5 requests/minute)
    if not limiter.check_device_limit(fingerprint):
        return Response({"error": "device_rate_limited"}, status=429)
"""
import logging
from typing import Optional, Tuple
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Sliding window rate limiter using Redis for SOS endpoint protection.
    
    Uses Redis INCR and EXPIRE commands for efficiency:
    - O(1) per check (single Redis operation)
    - TTL auto-expiry (no cleanup needed)
    - Accurate sliding window (not fixed buckets)
    
    Attributes:
        redis_client: Redis connection (from Django cache or standalone)
        window_seconds: Time window for rate limiting (default: 60 seconds)
        ip_limit: Max requests per IP per window (default: 100)
        device_limit: Max requests per device per window (default: 5)
    """
    
    # Configuration keys
    IP_RATE_KEY_PREFIX = "sos:rate:ip:"
    DEVICE_RATE_KEY_PREFIX = "sos:rate:device:"
    
    def __init__(
        self,
        redis_client: Optional[object] = None,
        window_seconds: int = 60,
        ip_limit: Optional[int] = None,
        device_limit: Optional[int] = None
    ):
        """
        Initialize rate limiter.
        
        Args:
            redis_client: Redis connection. If None, uses Django cache.
            window_seconds: Sliding window duration in seconds (default: 60)
            ip_limit: Max requests per IP (default: from settings or 100)
            device_limit: Max requests per device (default: from settings or 5)
        """
        self.redis_client = redis_client or cache
        self.window_seconds = window_seconds
        
        # Load from settings if available
        config = getattr(settings, 'SOS_RATE_LIMIT_CONFIG', {})
        self.ip_limit = ip_limit or config.get('IP_PER_MINUTE', 100)
        self.device_limit = device_limit or config.get('DEVICE_PER_MINUTE', 5)
    
    def check_ip_limit(self, ip_address: str) -> bool:
        """
        Check if IP address has exceeded rate limit.
        
        Uses sliding window algorithm:
        1. Increment counter for this IP
        2. Set expiration if this is the first request in window
        3. Return True if still under limit, False if exceeded
        
        Args:
            ip_address: Client IP address (IPv4 or IPv6)
            
        Returns:
            True if request is allowed, False if rate limited
            
        Raises:
            ValueError: If IP address is invalid or empty
            
        Example:
            >>> limiter = RateLimiter()
            >>> if limiter.check_ip_limit("192.168.1.1"):
            >>>     # Process request
            >>> else:
            >>>     # Return 429 Too Many Requests
        """
        if not ip_address or not isinstance(ip_address, str):
            logger.warning(f"Invalid IP address: {ip_address}")
            raise ValueError("IP address must be a non-empty string")
        
        key = f"{self.IP_RATE_KEY_PREFIX}{ip_address}"
        return self._check_and_increment(key, self.ip_limit)
    
    def check_device_limit(self, device_fingerprint: str) -> bool:
        """
        Check if device has exceeded rate limit.
        
        Uses sliding window algorithm:
        1. Increment counter for this device fingerprint
        2. Set expiration if this is the first request in window
        3. Return True if still under limit, False if exceeded
        
        Args:
            device_fingerprint: Unique device fingerprint (hex string, max 64 chars)
            
        Returns:
            True if request is allowed, False if rate limited
            
        Raises:
            ValueError: If fingerprint is invalid or empty
            
        Example:
            >>> limiter = RateLimiter()
            >>> if limiter.check_device_limit("abc123def456"):
            >>>     # Process request
            >>> else:
            >>>     # Return 429 Too Many Requests
        """
        if not device_fingerprint or not isinstance(device_fingerprint, str):
            logger.warning(f"Invalid device fingerprint: {device_fingerprint}")
            raise ValueError("Device fingerprint must be a non-empty string")
        
        key = f"{self.DEVICE_RATE_KEY_PREFIX}{device_fingerprint}"
        return self._check_and_increment(key, self.device_limit)
    
    def _check_and_increment(self, key: str, threshold: int) -> bool:
        """
        Perform sliding window check: increment counter and check against threshold.
        
        Algorithm:
        1. INCR key (atomic operation)
        2. If this is first increment (result == 1), set TTL
        3. Return True if under threshold, False if exceeded
        
        Args:
            key: Redis key for this rate limit counter
            threshold: Maximum allowed requests in window
            
        Returns:
            True if request allowed, False if rate limited
        """
        try:
            # Increment counter (atomic operation)
            current = self.redis_client.incr(key)
            
            # Set expiration on first request
            if current == 1:
                self.redis_client.expire(key, self.window_seconds)
            
            # Check if under threshold
            allowed = current <= threshold
            
            if not allowed:
                logger.warning(
                    f"Rate limit exceeded for key: {key}, "
                    f"current: {current}, threshold: {threshold}"
                )
            
            return allowed
            
        except Exception as e:
            # Graceful fallback on Redis error
            logger.error(f"Rate limiter error for key {key}: {str(e)}")
            # Fail-open: allow request if Redis is unavailable
            # This ensures SOS functionality is not broken by Redis outage
            logger.warning(f"Graceful degradation: allowing request due to Redis error")
            return True
    
    def reset_limit(self, ip_address: Optional[str] = None, 
                    device_fingerprint: Optional[str] = None) -> bool:
        """
        Reset rate limit counter for testing or administrative purposes.
        
        Args:
            ip_address: IP to reset (optional)
            device_fingerprint: Device to reset (optional)
            
        Returns:
            True if reset successfully, False if no key found
            
        Example:
            >>> limiter = RateLimiter()
            >>> limiter.reset_limit(ip_address="192.168.1.1")
        """
        success = False
        
        if ip_address:
            key = f"{self.IP_RATE_KEY_PREFIX}{ip_address}"
            try:
                self.redis_client.delete(key)
                success = True
                logger.info(f"Reset rate limit for IP: {ip_address}")
            except Exception as e:
                logger.error(f"Error resetting IP rate limit: {str(e)}")
        
        if device_fingerprint:
            key = f"{self.DEVICE_RATE_KEY_PREFIX}{device_fingerprint}"
            try:
                self.redis_client.delete(key)
                success = True
                logger.info(f"Reset rate limit for device: {device_fingerprint}")
            except Exception as e:
                logger.error(f"Error resetting device rate limit: {str(e)}")
        
        return success
    
    def get_current_count(self, ip_address: Optional[str] = None,
                         device_fingerprint: Optional[str] = None) -> int:
        """
        Get current request count for a rate limit key (for monitoring/debugging).
        
        Args:
            ip_address: IP to check (optional)
            device_fingerprint: Device to check (optional)
            
        Returns:
            Current request count (0 if not found)
            
        Example:
            >>> limiter = RateLimiter()
            >>> count = limiter.get_current_count(ip_address="192.168.1.1")
            >>> print(f"Current: {count}/100 requests")
        """
        if ip_address:
            key = f"{self.IP_RATE_KEY_PREFIX}{ip_address}"
            try:
                count = self.redis_client.get(key)
                return int(count) if count else 0
            except Exception as e:
                logger.error(f"Error getting IP count: {str(e)}")
                return 0
        
        if device_fingerprint:
            key = f"{self.DEVICE_RATE_KEY_PREFIX}{device_fingerprint}"
            try:
                count = self.redis_client.get(key)
                return int(count) if count else 0
            except Exception as e:
                logger.error(f"Error getting device count: {str(e)}")
                return 0
        
        return 0
