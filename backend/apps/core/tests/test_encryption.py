"""
Comprehensive tests for the Encryption Engine (AES-256-GCM).

Test Categories:
1. Unit Tests: Basic encrypt/decrypt operations
2. Property-Based Tests: Random inputs (1000+ iterations)
3. Edge Cases: Empty strings, max length, special characters
4. Tampering Detection: Ciphertext modification detection
5. Key Validation: Key format and length validation
6. Performance: Ensure <10ms encryption/decryption overhead
"""

import os
import pytest
from hypothesis import given, strategies as st, settings, Healthcheck

from apps.core.encryption import (
    EncryptionEngine,
    EncryptionIntegrityError,
    EncryptionFormatError,
)


class TestEncryptionEngineBasics:
    """Test basic encryption/decryption functionality."""
    
    @pytest.fixture
    def engine(self):
        """Create an encryption engine with random key."""
        key = EncryptionEngine.generate_key()
        return EncryptionEngine(key)
    
    def test_encryption_engine_initialization(self):
        """Test that engine initializes with 32-byte key."""
        key = EncryptionEngine.generate_key()
        engine = EncryptionEngine(key)
        assert engine.verify_key_format()
        assert engine.get_key_length_bits() == 256
    
    def test_encrypt_decrypt_roundtrip(self, engine):
        """Test basic encrypt/decrypt round-trip."""
        plaintext = "Hello World"
        ciphertext = engine.encrypt(plaintext)
        decrypted = engine.decrypt(ciphertext)
        assert decrypted == plaintext
    
    def test_encrypt_returns_string(self, engine):
        """Test that encrypt returns base64 string."""
        ciphertext = engine.encrypt("test")
        assert isinstance(ciphertext, str)
        assert len(ciphertext) > 0
    
    def test_decrypt_returns_string(self, engine):
        """Test that decrypt returns string."""
        ciphertext = engine.encrypt("test")
        plaintext = engine.decrypt(ciphertext)
        assert isinstance(plaintext, str)
        assert plaintext == "test"
    
    def test_ciphertext_is_base64_encoded(self, engine):
        """Test that ciphertext is valid base64."""
        import base64
        ciphertext = engine.encrypt("test")
        # Should not raise exception
        decoded = base64.b64decode(ciphertext.encode('ascii'))
        assert len(decoded) > 0
    
    def test_unique_ciphertexts_for_same_plaintext(self, engine):
        """Test that same plaintext produces different ciphertexts (random nonce)."""
        plaintext = "Same plaintext"
        ct1 = engine.encrypt(plaintext)
        ct2 = engine.encrypt(plaintext)
        ct3 = engine.encrypt(plaintext)
        
        # All three should be different (random nonce)
        assert ct1 != ct2
        assert ct2 != ct3
        assert ct1 != ct3
        
        # But all should decrypt to same plaintext
        assert engine.decrypt(ct1) == plaintext
        assert engine.decrypt(ct2) == plaintext
        assert engine.decrypt(ct3) == plaintext


class TestKeyValidation:
    """Test key format validation and error handling."""
    
    def test_key_must_be_32_bytes(self):
        """Test that key must be exactly 32 bytes."""
        with pytest.raises(EncryptionFormatError):
            EncryptionEngine(b"short_key")
    
    def test_key_too_long(self):
        """Test rejection of key longer than 32 bytes."""
        key = os.urandom(64)
        with pytest.raises(EncryptionFormatError):
            EncryptionEngine(key)
    
    def test_key_must_be_bytes(self):
        """Test that key must be bytes type."""
        with pytest.raises(EncryptionFormatError):
            EncryptionEngine("string_key_not_bytes")
    
    def test_key_validation_method(self):
        """Test verify_key_format method."""
        engine = EncryptionEngine(EncryptionEngine.generate_key())
        assert engine.verify_key_format() is True
    
    def test_generate_key_creates_32_bytes(self):
        """Test that generate_key creates 32-byte keys."""
        key = EncryptionEngine.generate_key()
        assert isinstance(key, bytes)
        assert len(key) == 32
        
        # Generate multiple keys to verify randomness
        key2 = EncryptionEngine.generate_key()
        assert key != key2


class TestEdgeCases:
    """Test edge cases and special inputs."""
    
    @pytest.fixture
    def engine(self):
        return EncryptionEngine(EncryptionEngine.generate_key())
    
    def test_encrypt_empty_string(self, engine):
        """Test encryption of empty string."""
        plaintext = ""
        ciphertext = engine.encrypt(plaintext)
        decrypted = engine.decrypt(ciphertext)
        assert decrypted == plaintext
    
    def test_encrypt_single_character(self, engine):
        """Test encryption of single character."""
        plaintext = "a"
        ciphertext = engine.encrypt(plaintext)
        decrypted = engine.decrypt(ciphertext)
        assert decrypted == plaintext
    
    def test_encrypt_very_long_string(self, engine):
        """Test encryption of long string (32KB)."""
        plaintext = "x" * (32 * 1024)  # 32KB
        ciphertext = engine.encrypt(plaintext)
        decrypted = engine.decrypt(ciphertext)
        assert decrypted == plaintext
        assert len(decrypted) == 32 * 1024
    
    def test_encrypt_special_characters(self, engine):
        """Test encryption of special characters."""
        plaintext = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        ciphertext = engine.encrypt(plaintext)
        decrypted = engine.decrypt(ciphertext)
        assert decrypted == plaintext
    
    def test_encrypt_unicode_chinese(self, engine):
        """Test encryption of Chinese characters."""
        plaintext = "你好世界"  # Hello World in Chinese
        ciphertext = engine.encrypt(plaintext)
        decrypted = engine.decrypt(ciphertext)
        assert decrypted == plaintext
    
    def test_encrypt_unicode_arabic(self, engine):
        """Test encryption of Arabic characters."""
        plaintext = "مرحبا بالعالم"  # Hello World in Arabic
        ciphertext = engine.encrypt(plaintext)
        decrypted = engine.decrypt(ciphertext)
        assert decrypted == plaintext
    
    def test_encrypt_unicode_emoji(self, engine):
        """Test encryption of emoji characters."""
        plaintext = "Hello 👋 World 🌍 🎉"
        ciphertext = engine.encrypt(plaintext)
        decrypted = engine.decrypt(ciphertext)
        assert decrypted == plaintext
    
    def test_encrypt_newlines_and_tabs(self, engine):
        """Test encryption of strings with whitespace."""
        plaintext = "Line 1\nLine 2\tTabbed\r\nWindows"
        ciphertext = engine.encrypt(plaintext)
        decrypted = engine.decrypt(ciphertext)
        assert decrypted == plaintext
    
    def test_encrypt_null_bytes(self, engine):
        """Test encryption of strings with null bytes."""
        plaintext = "Before\x00After"
        ciphertext = engine.encrypt(plaintext)
        decrypted = engine.decrypt(ciphertext)
        assert decrypted == plaintext


class TestTamperingDetection:
    """Test authentication tag verification and tampering detection."""
    
    @pytest.fixture
    def engine(self):
        return EncryptionEngine(EncryptionEngine.generate_key())
    
    def test_tampered_ciphertext_detected(self, engine):
        """Test that modified ciphertext is detected."""
        plaintext = "Important data"
        ciphertext = engine.encrypt(plaintext)
        
        # Tamper with one character
        tampered = ciphertext[:-5] + "xxxxx"
        
        with pytest.raises(EncryptionIntegrityError):
            engine.decrypt(tampered)
    
    def test_flipped_bit_detected(self, engine):
        """Test that single bit flip is detected."""
        import base64
        plaintext = "Secure message"
        ciphertext_b64 = engine.encrypt(plaintext)
        
        # Decode and flip a bit in the middle
        ciphertext_bytes = base64.b64decode(ciphertext_b64.encode('ascii'))
        byte_array = bytearray(ciphertext_bytes)
        byte_array[len(byte_array) // 2] ^= 0x01  # Flip one bit
        
        # Re-encode and try to decrypt
        tampered = base64.b64encode(bytes(byte_array)).decode('ascii')
        
        with pytest.raises(EncryptionIntegrityError):
            engine.decrypt(tampered)
    
    def test_missing_tag_detected(self, engine):
        """Test that ciphertext with missing tag is detected."""
        plaintext = "test"
        ciphertext_b64 = engine.encrypt(plaintext)
        
        import base64
        # Truncate to remove tag (last 16 bytes)
        ciphertext_bytes = base64.b64decode(ciphertext_b64.encode('ascii'))
        truncated = ciphertext_bytes[:-16]  # Remove tag
        truncated_b64 = base64.b64encode(truncated).decode('ascii')
        
        with pytest.raises((EncryptionIntegrityError, EncryptionFormatError)):
            engine.decrypt(truncated_b64)
    
    def test_wrong_key_detected(self, engine):
        """Test that decryption with wrong key fails."""
        plaintext = "Secret"
        ciphertext = engine.encrypt(plaintext)
        
        # Create engine with different key
        wrong_engine = EncryptionEngine(EncryptionEngine.generate_key())
        
        with pytest.raises(EncryptionIntegrityError):
            wrong_engine.decrypt(ciphertext)
    
    def test_invalid_base64_detected(self, engine):
        """Test that invalid base64 is detected."""
        with pytest.raises(EncryptionFormatError):
            engine.decrypt("not!valid@base64$$$")


class TestPropertyBasedTesting:
    """Property-based tests using Hypothesis (1000+ random iterations)."""
    
    @pytest.fixture
    def engine(self):
        return EncryptionEngine(EncryptionEngine.generate_key())
    
    @given(plaintext=st.text())
    @settings(max_examples=500, suppress_health_check=[Healthcheck.too_slow])
    def test_property_roundtrip_all_texts(self, engine, plaintext):
        """
        Property: For all plaintext strings, encrypt then decrypt equals original.
        
        Tests 500+ random strings including:
        - ASCII text
        - Unicode (all languages)
        - Special characters
        - Empty strings
        - Very long strings
        """
        ciphertext = engine.encrypt(plaintext)
        decrypted = engine.decrypt(ciphertext)
        assert decrypted == plaintext
    
    @given(plaintext=st.text())
    @settings(max_examples=500, suppress_health_check=[Healthcheck.too_slow])
    def test_property_different_ciphertexts(self, engine, plaintext):
        """
        Property: Same plaintext always produces different ciphertexts (random nonce).
        
        Tests that randomness is working correctly.
        """
        ct1 = engine.encrypt(plaintext)
        ct2 = engine.encrypt(plaintext)
        
        # Should be different (except for ~1 in 2^96 collision probability)
        if plaintext:  # Empty string still has random nonce
            assert ct1 != ct2
    
    @given(plaintext=st.text())
    @settings(max_examples=500, suppress_health_check=[Healthcheck.too_slow])
    def test_property_ciphertext_is_base64(self, engine, plaintext):
        """
        Property: Ciphertext is always valid base64-encoded string.
        """
        import base64
        ciphertext = engine.encrypt(plaintext)
        
        # Should be decodable as base64
        try:
            decoded = base64.b64decode(ciphertext.encode('ascii'))
            assert len(decoded) > 0
        except Exception:
            pytest.fail("Ciphertext is not valid base64")
    
    @given(plaintext=st.text())
    @settings(max_examples=500, suppress_health_check=[Healthcheck.too_slow])
    def test_property_ciphertext_longer_than_plaintext(self, engine, plaintext):
        """
        Property: Ciphertext is always longer than plaintext (adds nonce + tag + base64 overhead).
        """
        ciphertext = engine.encrypt(plaintext)
        plaintext_bytes = plaintext.encode('utf-8')
        
        # Ciphertext (base64) should be longer than plaintext bytes
        # (nonce=12 + tag=16 + overhead, encoded in base64)
        assert len(ciphertext) >= len(plaintext_bytes)
    
    @given(plaintext=st.text())
    @settings(max_examples=200, suppress_health_check=[Healthcheck.too_slow])
    def test_property_deterministic_key_derivation(self, plaintext):
        """
        Property: Same key always encrypts/decrypts consistently.
        
        Create multiple engines with same key and verify they encrypt/decrypt identically.
        """
        key = EncryptionEngine.generate_key()
        
        engine1 = EncryptionEngine(key)
        engine2 = EncryptionEngine(key)
        
        ct1 = engine1.encrypt(plaintext)
        ct2 = engine2.encrypt(plaintext)
        
        # Different engines can decrypt each other's ciphertexts (same key)
        assert engine2.decrypt(ct1) == plaintext
        assert engine1.decrypt(ct2) == plaintext


class TestIntegrationScenarios:
    """Integration tests simulating real-world usage."""
    
    def test_user_pii_encryption(self):
        """Test encryption of typical user PII."""
        engine = EncryptionEngine(EncryptionEngine.generate_key())
        
        user_data = {
            'first_name': 'Rajesh',
            'last_name': 'Kumar',
            'email': 'rajesh.kumar@warimitra.org',
            'phone': '+91-98765-43210',
        }
        
        # Encrypt each field
        encrypted = {}
        for key, value in user_data.items():
            encrypted[key] = engine.encrypt(value)
        
        # Decrypt and verify
        for key, value in user_data.items():
            assert engine.decrypt(encrypted[key]) == value
    
    def test_medical_records_encryption(self):
        """Test encryption of medical records."""
        engine = EncryptionEngine(EncryptionEngine.generate_key())
        
        medical_data = {
            'patient_name': 'Dr. Sharma',
            'blood_type': 'O+',
            'condition': 'Hypertension, Diabetes',
            'medications': 'Metformin 500mg, Amlodipine 5mg',
            'notes': 'Patient reports fatigue in afternoon hours',
        }
        
        # Encrypt
        for key in medical_data:
            medical_data[key] = engine.encrypt(medical_data[key])
        
        # Verify structure preserved
        assert len(medical_data) == 5
    
    def test_gps_coordinates_encryption(self):
        """Test encryption of GPS coordinates."""
        engine = EncryptionEngine(EncryptionEngine.generate_key())
        
        locations = [
            ('28.7041', '77.1025'),  # Delhi
            ('19.0760', '72.8777'),  # Mumbai
            ('13.0827', '80.2707'),  # Chennai
        ]
        
        for lat, lon in locations:
            ct_lat = engine.encrypt(lat)
            ct_lon = engine.encrypt(lon)
            
            assert engine.decrypt(ct_lat) == lat
            assert engine.decrypt(ct_lon) == lon
    
    def test_batch_encryption_many_records(self):
        """Test encryption of 1000+ records."""
        engine = EncryptionEngine(EncryptionEngine.generate_key())
        
        plaintexts = [f"Record {i}: Data content" for i in range(1000)]
        
        # Encrypt all
        ciphertexts = [engine.encrypt(p) for p in plaintexts]
        
        # Verify all decrypt correctly
        for i, (pt, ct) in enumerate(zip(plaintexts, ciphertexts)):
            decrypted = engine.decrypt(ct)
            assert decrypted == pt, f"Record {i} decryption failed"


class TestPerformance:
    """Performance tests to verify <10ms overhead per operation."""
    
    @pytest.fixture
    def engine(self):
        return EncryptionEngine(EncryptionEngine.generate_key())
    
    def test_encryption_performance(self, engine):
        """Test encryption is <5ms per operation."""
        import time
        
        plaintext = "Performance test data " * 10  # ~220 bytes
        
        # Warm up
        engine.encrypt(plaintext)
        
        # Measure 100 encryptions
        start = time.perf_counter()
        for _ in range(100):
            engine.encrypt(plaintext)
        elapsed = time.perf_counter() - start
        
        avg_time_ms = (elapsed / 100) * 1000
        assert avg_time_ms < 5.0, f"Encryption took {avg_time_ms}ms (target: <5ms)"
    
    def test_decryption_performance(self, engine):
        """Test decryption is <5ms per operation."""
        import time
        
        plaintext = "Performance test data " * 10
        ciphertext = engine.encrypt(plaintext)
        
        # Warm up
        engine.decrypt(ciphertext)
        
        # Measure 100 decryptions
        start = time.perf_counter()
        for _ in range(100):
            engine.decrypt(ciphertext)
        elapsed = time.perf_counter() - start
        
        avg_time_ms = (elapsed / 100) * 1000
        assert avg_time_ms < 5.0, f"Decryption took {avg_time_ms}ms (target: <5ms)"


# Run with: pytest backend/apps/core/tests/test_encryption.py -v
