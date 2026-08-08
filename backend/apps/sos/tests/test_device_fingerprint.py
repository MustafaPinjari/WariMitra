"""
Unit Tests for Device Fingerprint Validator
Phase 1.2 Implementation: DDoS Protection

Test Coverage:
- Format validation (hex string, UUID, length)
- Fingerprint tracking and storage
- Database operations (get_or_create)
- Known fingerprint detection
- Error handling
"""
import pytest
from django.test import TestCase
from django.db import IntegrityError
from apps.sos.device_fingerprint import DeviceFingerprintValidator
from apps.sos.models import DeviceFingerprint


class TestDeviceFingerprintValidation(TestCase):
    """Test fingerprint format validation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.validator = DeviceFingerprintValidator()
    
    def test_valid_sha256_fingerprint(self):
        """Test valid 64-char SHA256 hex fingerprint"""
        fp = "abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789"
        assert self.validator.validate_fingerprint(fp) is True
    
    def test_valid_md5_fingerprint(self):
        """Test valid 32-char MD5 hex fingerprint"""
        fp = "5d41402abc4b2a76b9719d911017c592"
        assert self.validator.validate_fingerprint(fp) is True
    
    def test_valid_uuid_fingerprint(self):
        """Test valid UUID format fingerprint"""
        fp = "550e8400-e29b-41d4-a716-446655440000"
        assert self.validator.validate_fingerprint(fp) is True
    
    def test_fingerprint_too_short(self):
        """Test fingerprint shorter than MD5 (32 chars)"""
        fp = "abcdef01234567"  # 14 chars
        assert self.validator.validate_fingerprint(fp) is False
    
    def test_fingerprint_too_long(self):
        """Test fingerprint longer than max (64 chars)"""
        fp = "a" * 65  # 65 chars
        assert self.validator.validate_fingerprint(fp) is False
    
    def test_fingerprint_exactly_max_length(self):
        """Test fingerprint at exactly max length (64 chars)"""
        fp = "a" * 64
        assert self.validator.validate_fingerprint(fp) is True
    
    def test_empty_fingerprint(self):
        """Test empty fingerprint string"""
        assert self.validator.validate_fingerprint("") is False
    
    def test_none_fingerprint(self):
        """Test None fingerprint"""
        assert self.validator.validate_fingerprint(None) is False
    
    def test_fingerprint_with_invalid_characters(self):
        """Test fingerprint with non-hex characters"""
        fp = "xyz123def456" + "a" * 52  # Contains 'x', 'y', 'z'
        assert self.validator.validate_fingerprint(fp) is False
    
    def test_fingerprint_with_spaces(self):
        """Test fingerprint with spaces"""
        fp = "abcdef0123456789 abcdef0123456789abcdef0123456789abcdef0123456789"
        assert self.validator.validate_fingerprint(fp) is False
    
    def test_fingerprint_case_insensitive(self):
        """Test that fingerprint validation is case-insensitive"""
        fp_upper = "ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789"
        fp_lower = "abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789"
        
        assert self.validator.validate_fingerprint(fp_upper) is True
        assert self.validator.validate_fingerprint(fp_lower) is True
    
    def test_fingerprint_not_string(self):
        """Test non-string fingerprint types"""
        assert self.validator.validate_fingerprint(12345) is False
        assert self.validator.validate_fingerprint([]) is False
        assert self.validator.validate_fingerprint({}) is False
    
    def test_static_method_validation(self):
        """Test static method for validation"""
        fp = "abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789"
        assert DeviceFingerprintValidator.validate_fingerprint_format(fp) is True


class TestDeviceFingerprintTracking(TestCase):
    """Test fingerprint tracking and storage"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.validator = DeviceFingerprintValidator()
        DeviceFingerprint.objects.all().delete()
    
    def test_track_new_fingerprint(self):
        """Test tracking a new fingerprint"""
        fp = "abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789"
        
        success, error = self.validator.track_fingerprint(
            fingerprint=fp,
            ip_address="192.168.1.1",
            user_agent="MobileApp/1.0",
            device_model="iPhone12",
            app_version="1.2.3",
            os_version="14.5"
        )
        
        assert success is True
        assert error is None
        
        # Verify stored in database
        obj = DeviceFingerprint.objects.get(fingerprint=fp)
        assert obj.ip_address == "192.168.1.1"
        assert obj.device_model == "iPhone12"
        assert obj.app_version == "1.2.3"
    
    def test_track_duplicate_fingerprint(self):
        """Test tracking duplicate fingerprint (should not error)"""
        fp = "abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789"
        
        # First tracking
        success1, error1 = self.validator.track_fingerprint(
            fingerprint=fp,
            ip_address="192.168.1.1"
        )
        assert success1 is True
        
        # Second tracking (duplicate)
        success2, error2 = self.validator.track_fingerprint(
            fingerprint=fp,
            ip_address="192.168.1.2"  # Different IP
        )
        assert success2 is True
        
        # Should only have one record
        assert DeviceFingerprint.objects.filter(fingerprint=fp).count() == 1
    
    def test_track_invalid_fingerprint(self):
        """Test tracking invalid fingerprint format"""
        success, error = self.validator.track_fingerprint(
            fingerprint="invalid!",
            ip_address="192.168.1.1"
        )
        
        assert success is False
        assert error is not None
    
    def test_track_with_minimal_info(self):
        """Test tracking with only required fields"""
        fp = "abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789"
        
        success, error = self.validator.track_fingerprint(
            fingerprint=fp,
            ip_address="192.168.1.1"
        )
        
        assert success is True
        assert error is None
        
        obj = DeviceFingerprint.objects.get(fingerprint=fp)
        assert obj.ip_address == "192.168.1.1"
        assert obj.device_model == ""
        assert obj.app_version == ""
    
    def test_track_with_full_info(self):
        """Test tracking with all optional fields"""
        fp = "abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789"
        
        success, error = self.validator.track_fingerprint(
            fingerprint=fp,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            device_model="Samsung Galaxy S21",
            app_version="2.1.0",
            os_version="11.0"
        )
        
        assert success is True
        
        obj = DeviceFingerprint.objects.get(fingerprint=fp)
        assert obj.user_agent == "Mozilla/5.0"
        assert obj.device_model == "Samsung Galaxy S21"
        assert obj.app_version == "2.1.0"
        assert obj.os_version == "11.0"
    
    def test_multiple_different_fingerprints(self):
        """Test tracking multiple different fingerprints"""
        fp1 = "abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789"
        fp2 = "fedcba9876543210fedcba9876543210fedcba9876543210fedcba9876543210"
        
        success1, _ = self.validator.track_fingerprint(
            fingerprint=fp1,
            ip_address="192.168.1.1"
        )
        success2, _ = self.validator.track_fingerprint(
            fingerprint=fp2,
            ip_address="192.168.1.2"
        )
        
        assert success1 is True
        assert success2 is True
        assert DeviceFingerprint.objects.count() == 2


class TestDeviceFingerprintRetrieval(TestCase):
    """Test retrieval of fingerprint information"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.validator = DeviceFingerprintValidator()
        DeviceFingerprint.objects.all().delete()
        
        # Create a test fingerprint
        self.fp = "abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789"
        DeviceFingerprint.objects.create(
            fingerprint=self.fp,
            ip_address="192.168.1.1",
            device_model="iPhone12",
            app_version="1.2.3"
        )
    
    def test_get_fingerprint_info_existing(self):
        """Test retrieving info for existing fingerprint"""
        info = self.validator.get_fingerprint_info(self.fp)
        
        assert info is not None
        assert info['fingerprint'] == self.fp
        assert info['ip_address'] == "192.168.1.1"
        assert info['device_model'] == "iPhone12"
        assert info['app_version'] == "1.2.3"
        assert 'created_at' in info
    
    def test_get_fingerprint_info_not_found(self):
        """Test retrieving info for non-existent fingerprint"""
        info = self.validator.get_fingerprint_info("nonexistent")
        
        assert info is None
    
    def test_is_fingerprint_known_true(self):
        """Test that known fingerprint is detected"""
        is_known = self.validator.is_fingerprint_known(self.fp)
        
        assert is_known is True
    
    def test_is_fingerprint_known_false(self):
        """Test that unknown fingerprint is not detected"""
        is_known = self.validator.is_fingerprint_known("unknown_fp_" + "a" * 50)
        
        assert is_known is False
    
    def test_count_fingerprints(self):
        """Test fingerprint counter"""
        # Should have 1 from setUp
        count = self.validator.count_fingerprints()
        assert count == 1
        
        # Add another
        fp2 = "fedcba9876543210fedcba9876543210fedcba9876543210fedcba9876543210"
        DeviceFingerprint.objects.create(
            fingerprint=fp2,
            ip_address="192.168.1.2"
        )
        
        count = self.validator.count_fingerprints()
        assert count == 2


class TestDeviceFingerprintEdgeCases(TestCase):
    """Test edge cases and error conditions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.validator = DeviceFingerprintValidator()
        DeviceFingerprint.objects.all().delete()
    
    def test_track_with_none_optional_fields(self):
        """Test tracking with None for optional fields"""
        fp = "abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789"
        
        success, error = self.validator.track_fingerprint(
            fingerprint=fp,
            ip_address="192.168.1.1",
            user_agent=None,
            device_model=None,
            app_version=None,
            os_version=None
        )
        
        assert success is True
        assert error is None
    
    def test_track_with_empty_optional_fields(self):
        """Test tracking with empty strings for optional fields"""
        fp = "abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789"
        
        success, error = self.validator.track_fingerprint(
            fingerprint=fp,
            ip_address="192.168.1.1",
            user_agent="",
            device_model="",
            app_version="",
            os_version=""
        )
        
        assert success is True
    
    def test_fingerprint_boundary_lengths(self):
        """Test fingerprints at boundary lengths"""
        # 32 chars (minimum valid)
        fp_min = "a" * 32
        assert self.validator.validate_fingerprint(fp_min) is True
        
        # 31 chars (too short)
        fp_too_short = "a" * 31
        assert self.validator.validate_fingerprint(fp_too_short) is False
        
        # 64 chars (maximum valid)
        fp_max = "a" * 64
        assert self.validator.validate_fingerprint(fp_max) is True
        
        # 65 chars (too long)
        fp_too_long = "a" * 65
        assert self.validator.validate_fingerprint(fp_too_long) is False
    
    def test_special_characters_rejection(self):
        """Test that special characters are rejected"""
        invalid_fps = [
            "abc!def@ghi#jkl$mno%pqr^stu*vwx(yz0123456789abcdefghijklmnopqrstuv",
            "abc\ndef" + "a" * 56,  # Newline
            "abc def" + "a" * 56,   # Space
            "abc/def" + "a" * 56,   # Slash
        ]
        
        for fp in invalid_fps:
            assert self.validator.validate_fingerprint(fp) is False
    
    def test_sql_injection_fingerprint(self):
        """Test that SQL injection attempts in fingerprint are rejected"""
        malicious_fps = [
            "'; DROP TABLE devices; --" + "a" * 30,
            "1' OR '1'='1" + "a" * 50,
        ]
        
        for fp in malicious_fps:
            assert self.validator.validate_fingerprint(fp) is False
