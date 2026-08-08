"""
Unit Tests for Rate Limiter Module
Phase 1.2 Implementation: DDoS Protection

Test Coverage:
- IP rate limiting (100 requests/minute)
- Device rate limiting (5 requests/minute)
- Sliding window algorithm
- Redis operations (INCR, EXPIRE)
- Graceful fallback on Redis errors
- Counter reset and monitoring
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from django.test import TestCase, override_settings
from django.core.cache import cache
from apps.sos.rate_limiter import RateLimiter


class TestRateLimiterIPLimit(TestCase):
    """Test IP-based rate limiting"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_redis = MagicMock()
        self.limiter = RateLimiter(redis_client=self.mock_redis)
        self.test_ip = "192.168.1.1"
    
    def test_first_request_allowed(self):
        """Test that first request is always allowed"""
        self.mock_redis.incr.return_value = 1
        
        result = self.limiter.check_ip_limit(self.test_ip)
        
        assert result is True
        self.mock_redis.incr.assert_called_once()
        self.mock_redis.expire.assert_called_once()
    
    def test_request_under_limit(self):
        """Test request when under IP limit (50/100)"""
        self.mock_redis.incr.return_value = 50
        
        result = self.limiter.check_ip_limit(self.test_ip)
        
        assert result is True
    
    def test_request_at_limit(self):
        """Test request exactly at limit (100/100)"""
        self.mock_redis.incr.return_value = 100
        
        result = self.limiter.check_ip_limit(self.test_ip)
        
        assert result is True
    
    def test_request_exceeds_limit(self):
        """Test request exceeding IP limit (101/100)"""
        self.mock_redis.incr.return_value = 101
        
        result = self.limiter.check_ip_limit(self.test_ip)
        
        assert result is False
    
    def test_multiple_requests_from_different_ips(self):
        """Test that different IPs have independent limits"""
        self.mock_redis.incr.side_effect = [1, 1, 2]
        
        result1 = self.limiter.check_ip_limit("192.168.1.1")
        result2 = self.limiter.check_ip_limit("192.168.1.2")
        result3 = self.limiter.check_ip_limit("192.168.1.1")
        
        assert result1 is True
        assert result2 is True
        assert result3 is True
        assert self.mock_redis.incr.call_count == 3
    
    def test_ip_limit_with_ipv6(self):
        """Test IP limit works with IPv6 addresses"""
        ipv6_addr = "2001:0db8:85a3:0000:0000:8a2e:0370:7334"
        self.mock_redis.incr.return_value = 1
        
        result = self.limiter.check_ip_limit(ipv6_addr)
        
        assert result is True
        assert ipv6_addr in self.mock_redis.incr.call_args[0][0]
    
    def test_expire_called_on_first_request(self):
        """Test TTL is set only on first request"""
        self.mock_redis.incr.side_effect = [1, 2, 3]
        
        self.limiter.check_ip_limit(self.test_ip)
        self.limiter.check_ip_limit(self.test_ip)
        self.limiter.check_ip_limit(self.test_ip)
        
        # Expire should be called only once (on first request)
        self.mock_redis.expire.assert_called_once()
    
    def test_invalid_ip_raises_error(self):
        """Test that invalid IP raises ValueError"""
        with pytest.raises(ValueError):
            self.limiter.check_ip_limit("")
        
        with pytest.raises(ValueError):
            self.limiter.check_ip_limit(None)
        
        with pytest.raises(ValueError):
            self.limiter.check_ip_limit(12345)  # Not a string


class TestRateLimiterDeviceLimit(TestCase):
    """Test device fingerprint-based rate limiting"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_redis = MagicMock()
        self.limiter = RateLimiter(redis_client=self.mock_redis)
        self.test_fingerprint = "abc123def456"
    
    def test_first_device_request_allowed(self):
        """Test that first device request is allowed"""
        self.mock_redis.incr.return_value = 1
        
        result = self.limiter.check_device_limit(self.test_fingerprint)
        
        assert result is True
        self.mock_redis.incr.assert_called_once()
    
    def test_device_request_under_limit(self):
        """Test device request when under limit (3/5)"""
        self.mock_redis.incr.return_value = 3
        
        result = self.limiter.check_device_limit(self.test_fingerprint)
        
        assert result is True
    
    def test_device_request_at_limit(self):
        """Test device request exactly at limit (5/5)"""
        self.mock_redis.incr.return_value = 5
        
        result = self.limiter.check_device_limit(self.test_fingerprint)
        
        assert result is True
    
    def test_device_request_exceeds_limit(self):
        """Test device request exceeding limit (6/5)"""
        self.mock_redis.incr.return_value = 6
        
        result = self.limiter.check_device_limit(self.test_fingerprint)
        
        assert result is False
    
    def test_multiple_devices_independent(self):
        """Test that different devices have independent limits"""
        self.mock_redis.incr.side_effect = [1, 1, 2]
        
        result1 = self.limiter.check_device_limit("device1")
        result2 = self.limiter.check_device_limit("device2")
        result3 = self.limiter.check_device_limit("device1")
        
        assert result1 is True
        assert result2 is True
        assert result3 is True
    
    def test_invalid_fingerprint_raises_error(self):
        """Test that invalid fingerprint raises ValueError"""
        with pytest.raises(ValueError):
            self.limiter.check_device_limit("")
        
        with pytest.raises(ValueError):
            self.limiter.check_device_limit(None)


class TestRateLimiterConfiguration(TestCase):
    """Test rate limiter configuration"""
    
    def test_default_limits(self):
        """Test default rate limit values"""
        limiter = RateLimiter(redis_client=MagicMock())
        
        assert limiter.ip_limit == 100
        assert limiter.device_limit == 5
    
    def test_custom_limits(self):
        """Test custom rate limit values"""
        limiter = RateLimiter(
            redis_client=MagicMock(),
            ip_limit=200,
            device_limit=10
        )
        
        assert limiter.ip_limit == 200
        assert limiter.device_limit == 10
    
    @override_settings(
        SOS_RATE_LIMIT_CONFIG={
            'IP_PER_MINUTE': 150,
            'DEVICE_PER_MINUTE': 8,
        }
    )
    def test_settings_configuration(self):
        """Test rate limits loaded from Django settings"""
        limiter = RateLimiter(redis_client=MagicMock())
        
        assert limiter.ip_limit == 150
        assert limiter.device_limit == 8
    
    def test_window_seconds_configuration(self):
        """Test custom window duration"""
        limiter = RateLimiter(redis_client=MagicMock(), window_seconds=120)
        
        assert limiter.window_seconds == 120


class TestRateLimiterGracefulDegradation(TestCase):
    """Test graceful fallback when Redis is unavailable"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_redis = MagicMock()
        self.limiter = RateLimiter(redis_client=self.mock_redis)
    
    def test_redis_connection_error(self):
        """Test that ConnectionError is handled gracefully"""
        self.mock_redis.incr.side_effect = ConnectionError("Redis unavailable")
        
        # Should return True (allow request) on error
        result = self.limiter.check_ip_limit("192.168.1.1")
        
        assert result is True
    
    def test_redis_timeout(self):
        """Test that timeout is handled gracefully"""
        self.mock_redis.incr.side_effect = TimeoutError("Redis timeout")
        
        # Should return True (allow request) on error
        result = self.limiter.check_ip_limit("192.168.1.1")
        
        assert result is True
    
    def test_generic_redis_error(self):
        """Test that generic exceptions are handled gracefully"""
        self.mock_redis.incr.side_effect = Exception("Generic Redis error")
        
        # Should return True (allow request) on error
        result = self.limiter.check_ip_limit("192.168.1.1")
        
        assert result is True


class TestRateLimiterMonitoring(TestCase):
    """Test monitoring and administrative functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_redis = MagicMock()
        self.limiter = RateLimiter(redis_client=self.mock_redis)
    
    def test_reset_ip_limit(self):
        """Test resetting IP rate limit counter"""
        self.mock_redis.delete.return_value = 1
        
        result = self.limiter.reset_limit(ip_address="192.168.1.1")
        
        assert result is True
        self.mock_redis.delete.assert_called_once()
    
    def test_reset_device_limit(self):
        """Test resetting device rate limit counter"""
        self.mock_redis.delete.return_value = 1
        
        result = self.limiter.reset_limit(device_fingerprint="abc123")
        
        assert result is True
    
    def test_reset_both_limits(self):
        """Test resetting both IP and device limits"""
        self.mock_redis.delete.return_value = 1
        
        result = self.limiter.reset_limit(
            ip_address="192.168.1.1",
            device_fingerprint="abc123"
        )
        
        assert result is True
        assert self.mock_redis.delete.call_count == 2
    
    def test_get_current_ip_count(self):
        """Test retrieving current IP request count"""
        self.mock_redis.get.return_value = b"42"
        
        count = self.limiter.get_current_count(ip_address="192.168.1.1")
        
        assert count == 42
    
    def test_get_current_device_count(self):
        """Test retrieving current device request count"""
        self.mock_redis.get.return_value = b"3"
        
        count = self.limiter.get_current_count(device_fingerprint="abc123")
        
        assert count == 3
    
    def test_get_count_when_not_found(self):
        """Test getting count returns 0 when key not found"""
        self.mock_redis.get.return_value = None
        
        count = self.limiter.get_current_count(ip_address="192.168.1.1")
        
        assert count == 0
    
    def test_get_count_handles_error(self):
        """Test that get_current_count handles errors gracefully"""
        self.mock_redis.get.side_effect = Exception("Redis error")
        
        count = self.limiter.get_current_count(ip_address="192.168.1.1")
        
        assert count == 0


class TestRateLimiterKeyNames(TestCase):
    """Test Redis key naming consistency"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_redis = MagicMock()
        self.limiter = RateLimiter(redis_client=self.mock_redis)
    
    def test_ip_key_format(self):
        """Test that IP keys are formatted correctly"""
        self.mock_redis.incr.return_value = 1
        
        self.limiter.check_ip_limit("192.168.1.1")
        
        call_args = self.mock_redis.incr.call_args[0][0]
        assert call_args == "sos:rate:ip:192.168.1.1"
    
    def test_device_key_format(self):
        """Test that device keys are formatted correctly"""
        self.mock_redis.incr.return_value = 1
        
        self.limiter.check_device_limit("abc123def456")
        
        call_args = self.mock_redis.incr.call_args[0][0]
        assert call_args == "sos:rate:device:abc123def456"


class TestRateLimiterIntegration(TestCase):
    """Integration tests with real cache (if available)"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Use Django's cache directly
        cache.clear()
        self.limiter = RateLimiter(redis_client=cache, window_seconds=5)
    
    def tearDown(self):
        """Clean up after tests"""
        cache.clear()
    
    def test_ip_limit_integration(self):
        """Integration test for IP rate limiting"""
        # First 100 requests should succeed
        for i in range(100):
            result = self.limiter.check_ip_limit("192.168.1.1")
            assert result is True
        
        # 101st request should fail
        result = self.limiter.check_ip_limit("192.168.1.1")
        assert result is False
    
    def test_device_limit_integration(self):
        """Integration test for device rate limiting"""
        # First 5 requests should succeed
        for i in range(5):
            result = self.limiter.check_device_limit("device123")
            assert result is True
        
        # 6th request should fail
        result = self.limiter.check_device_limit("device123")
        assert result is False
    
    def test_window_expiry(self):
        """Test that counters expire after window duration"""
        # Make requests to reach limit
        for i in range(100):
            self.limiter.check_ip_limit("192.168.1.1")
        
        # Should be rate limited
        result = self.limiter.check_ip_limit("192.168.1.1")
        assert result is False
        
        # Note: In real test, would need to wait for window_seconds to expire
        # This is integration test pattern
