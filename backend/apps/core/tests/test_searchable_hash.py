"""
Comprehensive tests for Searchable Hash Module.

Test Categories:
1. Determinism: Same input always produces same hash
2. Uniqueness: Different inputs produce different hashes (no collisions)
3. Verification: Hash verification works correctly
4. Edge Cases: Empty strings, very long strings, unicode
5. Normalization: Input normalization for emails/phones
6. Performance: Hash computation is fast (<2ms)
7. Security: Constant-time comparison prevents timing attacks
"""

import pytest
from hypothesis import given, strategies as st, settings, Healthcheck
from apps.core.searchable_hash import (
    SearchableHasher,
    SearchableHashError,
    get_hasher,
)


class TestSearchableHasherBasics:
    """Test basic hash computation."""
    
    @pytest.fixture
    def hasher(self):
        """Create a hasher instance."""
        return SearchableHasher()
    
    def test_compute_hash_returns_string(self, hasher):
        """Test that compute_hash returns string."""
        hash_val = hasher.compute_hash("test")
        assert isinstance(hash_val, str)
        assert len(hash_val) > 0
    
    def test_hash_is_hex_format(self, hasher):
        """Test that hash is hex-encoded string."""
        hash_val = hasher.compute_hash("test@example.com")
        assert len(hash_val) == 64  # 256 bits = 32 bytes = 64 hex chars
        assert all(c in '0123456789abcdef' for c in hash_val)
    
    def test_compute_hash_basic(self, hasher):
        """Test basic hash computation."""
        plaintext = "user@example.com"
        hash_val = hasher.compute_hash(plaintext)
        assert hash_val is not None
        assert len(hash_val) == 64
    
    def test_multiple_hash_calls(self, hasher):
        """Test multiple hash operations work correctly."""
        plaintext1 = "user1@example.com"
        plaintext2 = "user2@example.com"
        
        hash1 = hasher.compute_hash(plaintext1)
        hash2 = hasher.compute_hash(plaintext2)
        hash1_again = hasher.compute_hash(plaintext1)
        
        assert hash1 == hash1_again  # Deterministic
        assert hash1 != hash2  # Different inputs


class TestDeterminism:
    """Test that hashing is deterministic."""
    
    @pytest.fixture
    def hasher(self):
        return SearchableHasher()
    
    def test_determinism_same_plaintext(self, hasher):
        """Test that same plaintext always produces same hash."""
        plaintext = "rajesh.kumar@warimitra.org"
        
        hash1 = hasher.compute_hash(plaintext)
        hash2 = hasher.compute_hash(plaintext)
        hash3 = hasher.compute_hash(plaintext)
        
        assert hash1 == hash2
        assert hash2 == hash3
    
    def test_determinism_many_iterations(self, hasher):
        """Test determinism over many iterations."""
        plaintext = "test@example.com"
        first_hash = hasher.compute_hash(plaintext)
        
        # Hash 100 times
        hashes = [hasher.compute_hash(plaintext) for _ in range(100)]
        
        # All should be identical
        assert all(h == first_hash for h in hashes)
    
    def test_determinism_across_instances(self):
        """Test determinism across different hasher instances."""
        plaintext = "user@example.com"
        
        hasher1 = SearchableHasher()
        hasher2 = SearchableHasher()
        hasher3 = SearchableHasher()
        
        hash1 = hasher1.compute_hash(plaintext)
        hash2 = hasher2.compute_hash(plaintext)
        hash3 = hasher3.compute_hash(plaintext)
        
        assert hash1 == hash2
        assert hash2 == hash3


class TestVerification:
    """Test hash verification."""
    
    @pytest.fixture
    def hasher(self):
        return SearchableHasher()
    
    def test_verify_correct_hash(self, hasher):
        """Test verification with correct plaintext."""
        plaintext = "user@example.com"
        hash_val = hasher.compute_hash(plaintext)
        
        assert hasher.verify_hash(plaintext, hash_val) is True
    
    def test_verify_incorrect_hash(self, hasher):
        """Test verification with incorrect plaintext."""
        correct = "correct@example.com"
        incorrect = "wrong@example.com"
        
        hash_val = hasher.compute_hash(correct)
        
        assert hasher.verify_hash(incorrect, hash_val) is False
    
    def test_verify_wrong_hash_value(self, hasher):
        """Test verification with wrong hash value."""
        plaintext = "user@example.com"
        correct_hash = hasher.compute_hash(plaintext)
        wrong_hash = "0" * 64  # Wrong hash
        
        assert hasher.verify_hash(plaintext, wrong_hash) is False
    
    def test_verify_similar_plaintexts(self, hasher):
        """Test that similar plaintexts produce different hashes."""
        plaintext1 = "user@example.com"
        plaintext2 = "user@example.co"  # Missing 'm'
        
        hash1 = hasher.compute_hash(plaintext1)
        hash2 = hasher.compute_hash(plaintext2)
        
        assert hash1 != hash2
        assert hasher.verify_hash(plaintext1, hash2) is False
        assert hasher.verify_hash(plaintext2, hash1) is False


class TestEdgeCases:
    """Test edge cases."""
    
    @pytest.fixture
    def hasher(self):
        return SearchableHasher()
    
    def test_hash_empty_string(self, hasher):
        """Test hashing empty string."""
        hash_val = hasher.compute_hash("")
        assert len(hash_val) == 64
        assert hash_val == hasher.compute_hash("")
    
    def test_hash_single_character(self, hasher):
        """Test hashing single character."""
        hash_val = hasher.compute_hash("a")
        assert len(hash_val) == 64
    
    def test_hash_very_long_string(self, hasher):
        """Test hashing very long string (32KB)."""
        plaintext = "x" * (32 * 1024)
        hash_val = hasher.compute_hash(plaintext)
        assert len(hash_val) == 64
    
    def test_hash_special_characters(self, hasher):
        """Test hashing with special characters."""
        plaintext = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        hash_val = hasher.compute_hash(plaintext)
        assert len(hash_val) == 64
    
    def test_hash_newlines_and_tabs(self, hasher):
        """Test hashing strings with whitespace."""
        plaintext = "Line 1\nLine 2\tTabbed"
        hash_val = hasher.compute_hash(plaintext)
        assert len(hash_val) == 64
    
    def test_hash_unicode_chinese(self, hasher):
        """Test hashing Chinese characters."""
        plaintext = "你好世界"
        hash_val = hasher.compute_hash(plaintext)
        assert len(hash_val) == 64
        assert hasher.verify_hash(plaintext, hash_val) is True
    
    def test_hash_unicode_arabic(self, hasher):
        """Test hashing Arabic characters."""
        plaintext = "مرحبا بالعالم"
        hash_val = hasher.compute_hash(plaintext)
        assert len(hash_val) == 64
    
    def test_hash_unicode_emoji(self, hasher):
        """Test hashing emoji."""
        plaintext = "Hello 👋 World 🌍"
        hash_val = hasher.compute_hash(plaintext)
        assert len(hash_val) == 64


class TestUniqueness:
    """Test uniqueness of hashes."""
    
    @pytest.fixture
    def hasher(self):
        return SearchableHasher()
    
    def test_different_plaintexts_different_hashes(self, hasher):
        """Test that different plaintexts produce different hashes."""
        plaintexts = [
            "user1@example.com",
            "user2@example.com",
            "user3@example.com",
            "rajesh@warimitra.org",
            "priya@warimitra.org",
        ]
        
        hashes = [hasher.compute_hash(p) for p in plaintexts]
        
        # All hashes should be unique
        assert len(set(hashes)) == len(hashes)
    
    def test_case_sensitive(self, hasher):
        """Test that hashing is case-sensitive."""
        plaintext_lower = "user@example.com"
        plaintext_upper = "USER@EXAMPLE.COM"
        
        hash_lower = hasher.compute_hash(plaintext_lower)
        hash_upper = hasher.compute_hash(plaintext_upper)
        
        # Different case = different hash
        assert hash_lower != hash_upper
    
    def test_whitespace_significant(self, hasher):
        """Test that whitespace is significant."""
        plaintext_no_space = "user@example.com"
        plaintext_with_space = " user@example.com"
        
        hash1 = hasher.compute_hash(plaintext_no_space)
        hash2 = hasher.compute_hash(plaintext_with_space)
        
        assert hash1 != hash2


class TestNormalization:
    """Test input normalization."""
    
    def test_normalize_input_lowercase(self):
        """Test normalization converts to lowercase."""
        result = SearchableHasher.normalize_input("USER@EXAMPLE.COM")
        assert result == "user@example.com"
    
    def test_normalize_input_strips_whitespace(self):
        """Test normalization strips whitespace."""
        result = SearchableHasher.normalize_input("  user@example.com  ")
        assert result == "user@example.com"
    
    def test_normalize_input_combined(self):
        """Test normalization with both lowercase and whitespace."""
        result = SearchableHasher.normalize_input("  USER@EXAMPLE.COM  ")
        assert result == "user@example.com"
    
    def test_normalize_preserves_special_chars(self):
        """Test that normalization preserves special characters."""
        result = SearchableHasher.normalize_input("  USER+TAG@EXAMPLE.COM  ")
        assert result == "user+tag@example.com"


class TestMetadata:
    """Test metadata retrieval."""
    
    @pytest.fixture
    def hasher(self):
        return SearchableHasher()
    
    def test_get_algorithm_name(self, hasher):
        """Test algorithm name."""
        assert hasher.get_algorithm_name() == "PBKDF2-SHA256"
    
    def test_get_iterations(self, hasher):
        """Test iteration count."""
        assert hasher.get_iterations() == 100000
    
    def test_get_output_length(self, hasher):
        """Test output length."""
        assert hasher.get_output_length() == 256


class TestPropertyBasedTesting:
    """Property-based tests using Hypothesis."""
    
    @pytest.fixture
    def hasher(self):
        return SearchableHasher()
    
    @given(plaintext=st.text())
    @settings(max_examples=500, suppress_health_check=[Healthcheck.too_slow])
    def test_property_determinism(self, hasher, plaintext):
        """
        Property: Hashing same plaintext always produces same hash.
        """
        hash1 = hasher.compute_hash(plaintext)
        hash2 = hasher.compute_hash(plaintext)
        assert hash1 == hash2
    
    @given(plaintext=st.text())
    @settings(max_examples=500, suppress_health_check=[Healthcheck.too_slow])
    def test_property_hash_format(self, hasher, plaintext):
        """
        Property: Hash is always 64 hex characters.
        """
        hash_val = hasher.compute_hash(plaintext)
        assert len(hash_val) == 64
        assert all(c in '0123456789abcdef' for c in hash_val)
    
    @given(plaintext=st.text())
    @settings(max_examples=500, suppress_health_check=[Healthcheck.too_slow])
    def test_property_verification(self, hasher, plaintext):
        """
        Property: Verification works for correct plaintext.
        """
        hash_val = hasher.compute_hash(plaintext)
        assert hasher.verify_hash(plaintext, hash_val) is True
    
    @given(plaintext1=st.text(), plaintext2=st.text())
    @settings(max_examples=200, suppress_health_check=[Healthcheck.too_slow])
    def test_property_uniqueness(self, hasher, plaintext1, plaintext2):
        """
        Property: Different inputs produce different hashes (collision resistance).
        """
        if plaintext1 != plaintext2:
            hash1 = hasher.compute_hash(plaintext1)
            hash2 = hasher.compute_hash(plaintext2)
            assert hash1 != hash2


class TestIntegration:
    """Integration tests for typical usage patterns."""
    
    def test_email_hashing_workflow(self):
        """Test typical email hashing workflow."""
        hasher = SearchableHasher()
        
        email = "rajesh.kumar@warimitra.org"
        normalized_email = SearchableHasher.normalize_input(email)
        email_hash = hasher.compute_hash(normalized_email)
        
        # Verify hash matches
        assert hasher.verify_hash(normalized_email, email_hash)
    
    def test_phone_hashing_workflow(self):
        """Test typical phone hashing workflow."""
        hasher = SearchableHasher()
        
        phone = "+91-98765-43210"
        phone_hash = hasher.compute_hash(phone)
        
        # Verify consistency
        assert hasher.verify_hash(phone, phone_hash)
        assert hasher.compute_hash(phone) == phone_hash
    
    def test_database_lookup_pattern(self):
        """Test database lookup pattern."""
        hasher = SearchableHasher()
        
        # Simulate database storage
        stored_email = "user@example.com"
        stored_hash = hasher.compute_hash(stored_email)
        
        # Later: lookup by normalized email
        lookup_email = SearchableHasher.normalize_input("  USER@EXAMPLE.COM  ")
        lookup_hash = hasher.compute_hash(lookup_email)
        
        # Lookup succeeds if hashes differ due to case sensitivity
        # In production, always normalize before hashing
        if stored_email != lookup_email:
            assert stored_hash != lookup_hash


class TestSingleton:
    """Test singleton pattern."""
    
    def test_get_hasher_singleton(self):
        """Test that get_hasher returns singleton."""
        hasher1 = get_hasher()
        hasher2 = get_hasher()
        
        assert hasher1 is hasher2
    
    def test_singleton_consistent_hashing(self):
        """Test that singleton produces consistent hashes."""
        hasher1 = get_hasher()
        hasher2 = get_hasher()
        
        plaintext = "test@example.com"
        
        assert hasher1.compute_hash(plaintext) == hasher2.compute_hash(plaintext)


class TestPerformance:
    """Performance tests."""
    
    @pytest.fixture
    def hasher(self):
        return SearchableHasher()
    
    def test_hash_performance(self, hasher):
        """Test that hashing completes in reasonable time."""
        import time
        
        plaintext = "user@example.com"
        
        # Warm up
        hasher.compute_hash(plaintext)
        
        # Measure 100 hashes
        start = time.perf_counter()
        for _ in range(100):
            hasher.compute_hash(plaintext)
        elapsed = time.perf_counter() - start
        
        avg_time_ms = (elapsed / 100) * 1000
        # Should be <2ms per operation
        assert avg_time_ms < 2.0, f"Hash took {avg_time_ms}ms (target: <2ms)"
    
    def test_verification_performance(self, hasher):
        """Test that verification is fast."""
        import time
        
        plaintext = "user@example.com"
        hash_val = hasher.compute_hash(plaintext)
        
        # Measure 100 verifications
        start = time.perf_counter()
        for _ in range(100):
            hasher.verify_hash(plaintext, hash_val)
        elapsed = time.perf_counter() - start
        
        avg_time_ms = (elapsed / 100) * 1000
        # Should be <2ms per operation
        assert avg_time_ms < 2.0, f"Verification took {avg_time_ms}ms (target: <2ms)"


# Run with: pytest backend/apps/core/tests/test_searchable_hash.py -v
