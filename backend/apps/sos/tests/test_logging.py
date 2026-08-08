"""
Unit Tests for SOS Audit Logging
Phase 1.2 Implementation: DDoS Protection

Test Coverage:
- Basic audit log creation
- Convenience logging functions
- Error handling and graceful degradation
- Database entry verification
"""
import pytest
from django.test import TestCase
from django.utils import timezone
from apps.sos.logging import (
    log_sos_attempt,
    log_rate_limit_exceeded,
    log_geofence_violation,
    log_invalid_fingerprint,
)
from apps.sos.models import SOSAuditLog


class TestBasicLogging(TestCase):
    """Test basic SOS attempt logging"""
    
    def setUp(self):
        """Set up test fixtures"""
        SOSAuditLog.objects.all().delete()
    
    def test_log_successful_attempt(self):
        """Test logging a successful SOS attempt"""
        success = log_sos_attempt(
            sos_alert_id=123,
            ip_address="192.168.1.1",
            device_fingerprint="abc123def456" + "a" * 50,
            latitude=28.6139,
            longitude=77.2090,
            radius=1000,
            rate_limit_ip_status="PASS",
            rate_limit_device_status="PASS",
            geofence_status="PASS",
            result="SUCCESS"
        )
        
        assert success is True
        
        # Verify log entry created
        log_entry = SOSAuditLog.objects.get(
            device_fingerprint="abc123def456" + "a" * 50
        )
        assert log_entry.result == "SUCCESS"
        assert log_entry.sos_alert_id == 123
        assert log_entry.ip_address == "192.168.1.1"
        assert log_entry.latitude == 28.6139
        assert log_entry.longitude == 77.2090
        assert log_entry.radius == 1000
    
    def test_log_with_optional_fields(self):
        """Test logging with all optional fields"""
        fp = "abc123def456" + "a" * 50
        
        success = log_sos_attempt(
            sos_alert_id=456,
            ip_address="192.168.1.1",
            device_fingerprint=fp,
            latitude=19.0760,
            longitude=72.8777,
            radius=2000,
            rate_limit_ip_status="PASS",
            rate_limit_device_status="PASS",
            geofence_status="PASS",
            result="SUCCESS",
            user_id=789,
            device_model="iPhone12",
            app_version="1.2.3",
            user_agent="MobileApp/1.0"
        )
        
        assert success is True
        
        log_entry = SOSAuditLog.objects.get(device_fingerprint=fp)
        assert log_entry.user_id == 789
        assert log_entry.device_model == "iPhone12"
        assert log_entry.app_version == "1.2.3"
        assert log_entry.user_agent == "MobileApp/1.0"
    
    def test_log_with_reason(self):
        """Test logging with failure reason"""
        fp = "bcd234efg567" + "b" * 50
        
        success = log_sos_attempt(
            sos_alert_id=None,
            ip_address="192.168.1.2",
            device_fingerprint=fp,
            latitude=28.0,
            longitude=77.0,
            radius=None,
            rate_limit_ip_status="REJECT",
            rate_limit_device_status="PASS",
            geofence_status="PASS",
            result="RATE_LIMITED_IP",
            reason="Too many requests from this IP"
        )
        
        assert success is True
        
        log_entry = SOSAuditLog.objects.get(device_fingerprint=fp)
        assert log_entry.result == "RATE_LIMITED_IP"
        assert log_entry.reason == "Too many requests from this IP"
    
    def test_log_count_increases(self):
        """Test that each log increases entry count"""
        initial_count = SOSAuditLog.objects.count()
        
        log_sos_attempt(
            sos_alert_id=1,
            ip_address="192.168.1.1",
            device_fingerprint="fp1" + "a" * 58,
            latitude=28.0,
            longitude=77.0,
            radius=1000,
            rate_limit_ip_status="PASS",
            rate_limit_device_status="PASS",
            geofence_status="PASS",
            result="SUCCESS"
        )
        
        log_sos_attempt(
            sos_alert_id=2,
            ip_address="192.168.1.2",
            device_fingerprint="fp2" + "b" * 58,
            latitude=28.0,
            longitude=77.0,
            radius=1000,
            rate_limit_ip_status="PASS",
            rate_limit_device_status="PASS",
            geofence_status="PASS",
            result="SUCCESS"
        )
        
        assert SOSAuditLog.objects.count() == initial_count + 2


class TestRateLimitLogging(TestCase):
    """Test rate limit violation logging"""
    
    def setUp(self):
        """Set up test fixtures"""
        SOSAuditLog.objects.all().delete()
    
    def test_log_ip_rate_limit_exceeded(self):
        """Test logging IP rate limit exceeded"""
        fp = "ip_rate_fp" + "a" * 51
        
        success = log_rate_limit_exceeded(
            identifier="192.168.1.1",
            limit_type="IP",
            ip_address="192.168.1.1",
            device_fingerprint=fp,
            latitude=28.0,
            longitude=77.0
        )
        
        assert success is True
        
        log_entry = SOSAuditLog.objects.get(device_fingerprint=fp)
        assert log_entry.result == "RATE_LIMITED_IP"
        assert log_entry.rate_limit_ip_status == "REJECT"
        assert log_entry.rate_limit_device_status == "PASS"
        assert "rate limit exceeded" in log_entry.reason.lower()
    
    def test_log_device_rate_limit_exceeded(self):
        """Test logging device rate limit exceeded"""
        fp = "device_rate_fp" + "a" * 48
        
        success = log_rate_limit_exceeded(
            identifier=fp,
            limit_type="DEVICE",
            ip_address="192.168.1.1",
            device_fingerprint=fp,
            latitude=28.0,
            longitude=77.0
        )
        
        assert success is True
        
        log_entry = SOSAuditLog.objects.get(device_fingerprint=fp)
        assert log_entry.result == "RATE_LIMITED_DEVICE"
        assert log_entry.rate_limit_device_status == "REJECT"
        assert log_entry.rate_limit_ip_status == "PASS"
    
    def test_log_invalid_limit_type(self):
        """Test logging with invalid limit type"""
        success = log_rate_limit_exceeded(
            identifier="test",
            limit_type="INVALID",
            ip_address="192.168.1.1",
            device_fingerprint="fp" + "a" * 60,
            latitude=28.0,
            longitude=77.0
        )
        
        assert success is False


class TestGeofenceLogging(TestCase):
    """Test geofence violation logging"""
    
    def setUp(self):
        """Set up test fixtures"""
        SOSAuditLog.objects.all().delete()
    
    def test_log_geofence_violation(self):
        """Test logging geofence violation"""
        fp = "geofence_fp" + "a" * 50
        
        success = log_geofence_violation(
            ip_address="192.168.1.1",
            device_fingerprint=fp,
            latitude=52.52,  # Berlin
            longitude=13.40,
            reason="Location too far north"
        )
        
        assert success is True
        
        log_entry = SOSAuditLog.objects.get(device_fingerprint=fp)
        assert log_entry.result == "INVALID_LOCATION"
        assert log_entry.geofence_status == "REJECT"
        assert log_entry.rate_limit_ip_status == "PASS"
        assert log_entry.rate_limit_device_status == "PASS"
        assert "Location too far north" in log_entry.reason
    
    def test_log_geofence_with_all_options(self):
        """Test geofence logging with all optional fields"""
        fp = "geofence_full" + "a" * 48
        
        success = log_geofence_violation(
            ip_address="192.168.1.1",
            device_fingerprint=fp,
            latitude=52.52,
            longitude=13.40,
            reason="Latitude out of bounds",
            radius=5000,
            user_id=123,
            device_model="Samsung Galaxy",
            app_version="2.0.0",
            user_agent="SamsungBrowser/1.0"
        )
        
        assert success is True
        
        log_entry = SOSAuditLog.objects.get(device_fingerprint=fp)
        assert log_entry.radius == 5000
        assert log_entry.user_id == 123
        assert log_entry.device_model == "Samsung Galaxy"


class TestFingerprintLogging(TestCase):
    """Test invalid fingerprint logging"""
    
    def setUp(self):
        """Set up test fixtures"""
        SOSAuditLog.objects.all().delete()
    
    def test_log_invalid_fingerprint(self):
        """Test logging invalid fingerprint"""
        fp = "invalid_fp!"  # Invalid format
        
        success = log_invalid_fingerprint(
            ip_address="192.168.1.1",
            device_fingerprint=fp,
            latitude=28.0,
            longitude=77.0,
            reason="Fingerprint format invalid"
        )
        
        assert success is True
        
        log_entry = SOSAuditLog.objects.get(device_fingerprint=fp)
        assert log_entry.result == "INVALID_FINGERPRINT"
        assert "format invalid" in log_entry.reason.lower()
        assert log_entry.geofence_status == "PASS"
        assert log_entry.rate_limit_ip_status == "PASS"


class TestLoggingErrorHandling(TestCase):
    """Test error handling in logging"""
    
    def test_log_with_missing_ip(self):
        """Test logging with missing IP returns False"""
        success = log_sos_attempt(
            sos_alert_id=1,
            ip_address="",  # Empty IP
            device_fingerprint="fp" + "a" * 60,
            latitude=28.0,
            longitude=77.0,
            radius=1000,
            rate_limit_ip_status="PASS",
            rate_limit_device_status="PASS",
            geofence_status="PASS",
            result="SUCCESS"
        )
        
        assert success is False
    
    def test_log_with_missing_fingerprint(self):
        """Test logging with missing fingerprint returns False"""
        success = log_sos_attempt(
            sos_alert_id=1,
            ip_address="192.168.1.1",
            device_fingerprint="",  # Empty fingerprint
            latitude=28.0,
            longitude=77.0,
            radius=1000,
            rate_limit_ip_status="PASS",
            rate_limit_device_status="PASS",
            geofence_status="PASS",
            result="SUCCESS"
        )
        
        assert success is False
    
    def test_log_graceful_degradation(self):
        """Test that logging errors don't propagate exceptions"""
        # Try to log with None values for required fields
        try:
            success = log_sos_attempt(
                sos_alert_id=None,
                ip_address=None,
                device_fingerprint=None,
                latitude=28.0,
                longitude=77.0,
                radius=1000,
                rate_limit_ip_status="PASS",
                rate_limit_device_status="PASS",
                geofence_status="PASS",
                result="SUCCESS"
            )
            # Should return False, not raise exception
            assert success is False
        except Exception as e:
            pytest.fail(f"Logging raised exception: {e}")


class TestLoggingProperties(TestCase):
    """Test SOSAuditLog model properties"""
    
    def setUp(self):
        """Set up test fixtures"""
        SOSAuditLog.objects.all().delete()
    
    def test_is_success_property(self):
        """Test is_success property"""
        log_sos_attempt(
            sos_alert_id=1,
            ip_address="192.168.1.1",
            device_fingerprint="prop1" + "a" * 57,
            latitude=28.0,
            longitude=77.0,
            radius=1000,
            rate_limit_ip_status="PASS",
            rate_limit_device_status="PASS",
            geofence_status="PASS",
            result="SUCCESS"
        )
        
        entry = SOSAuditLog.objects.get(device_fingerprint="prop1" + "a" * 57)
        assert entry.is_success is True
    
    def test_is_rate_limited_property(self):
        """Test is_rate_limited property"""
        log_sos_attempt(
            sos_alert_id=None,
            ip_address="192.168.1.1",
            device_fingerprint="prop2" + "a" * 57,
            latitude=28.0,
            longitude=77.0,
            radius=None,
            rate_limit_ip_status="REJECT",
            rate_limit_device_status="PASS",
            geofence_status="PASS",
            result="RATE_LIMITED_IP"
        )
        
        entry = SOSAuditLog.objects.get(device_fingerprint="prop2" + "a" * 57)
        assert entry.is_rate_limited is True
        assert entry.is_success is False
    
    def test_is_geofence_violation_property(self):
        """Test is_geofence_violation property"""
        log_sos_attempt(
            sos_alert_id=None,
            ip_address="192.168.1.1",
            device_fingerprint="prop3" + "a" * 57,
            latitude=52.52,
            longitude=13.40,
            radius=None,
            rate_limit_ip_status="PASS",
            rate_limit_device_status="PASS",
            geofence_status="REJECT",
            result="INVALID_LOCATION"
        )
        
        entry = SOSAuditLog.objects.get(device_fingerprint="prop3" + "a" * 57)
        assert entry.is_geofence_violation is True
