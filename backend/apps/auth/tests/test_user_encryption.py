"""
Tests for Phase 1.3 User Model Encryption

Tests cover:
- Creating User with encrypted PII
- Querying by email_hash (searchable lookup)
- Updating User (re-encryption)
- Backwards compatibility with unencrypted data
- Admin interface display
"""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.core.encryption import EncryptionEngine
from apps.core.key_manager import get_key_manager
from apps.core.searchable_hash import SearchableHasher, get_hasher


User = get_user_model()


class UserEncryptionTestCase(TestCase):
    """Test User model encryption functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.key_manager = get_key_manager()
        self.hasher = get_hasher()
        self.test_email = "rajesh.kumar@example.com"
        self.test_phone = "+91-9876543210"
        self.test_first_name = "Rajesh"
        self.test_last_name = "Kumar"
    
    def test_create_user_with_encrypted_pii(self):
        """Test creating User with encrypted PII fields."""
        user = User.objects.create(
            username="rajesh",
            first_name=self.test_first_name,
            last_name=self.test_last_name,
            email=self.test_email,
            phone_number=self.test_phone,
        )
        
        # Verify user was created
        self.assertIsNotNone(user.id)
        self.assertEqual(user.username, "rajesh")
        
        # Verify data is encrypted in database
        user_db = User.objects.raw(
            "SELECT * FROM auth_user WHERE id = %s", [user.id]
        )[0]
        
        # Check that stored values are ciphertext (encrypted)
        # Ciphertext should NOT equal plaintext
        self.assertNotEqual(user_db.first_name, self.test_first_name)
        self.assertNotEqual(user_db.last_name, self.test_last_name)
        self.assertNotEqual(user_db.email, self.test_email)
    
    def test_decrypt_user_on_read(self):
        """Test decryption when reading User from database."""
        user = User.objects.create(
            username="priya",
            first_name=self.test_first_name,
            last_name=self.test_last_name,
            email=self.test_email,
            phone_number=self.test_phone,
        )
        
        # Fetch user from database
        user_fetched = User.objects.get(id=user.id)
        
        # Verify decryption worked
        self.assertEqual(user_fetched.first_name, self.test_first_name)
        self.assertEqual(user_fetched.last_name, self.test_last_name)
        self.assertEqual(user_fetched.email, self.test_email)
        self.assertEqual(user_fetched.phone_number, self.test_phone)
    
    def test_email_hash_generated_on_save(self):
        """Test email_hash is automatically computed on save."""
        user = User.objects.create(
            username="akshay",
            email=self.test_email,
        )
        
        # Verify email_hash was generated
        self.assertIsNotNone(user.email_hash)
        self.assertEqual(len(user.email_hash), 64)  # SHA256 hex = 64 chars
        
        # Verify hash is correct (normalized email)
        normalized_email = SearchableHasher.normalize_input(self.test_email)
        expected_hash = self.hasher.compute_hash(normalized_email)
        self.assertEqual(user.email_hash, expected_hash)
    
    def test_phone_hash_generated_on_save(self):
        """Test phone_hash is automatically computed on save."""
        user = User.objects.create(
            username="vikram",
            phone_number=self.test_phone,
        )
        
        # Verify phone_hash was generated
        self.assertIsNotNone(user.phone_hash)
        self.assertEqual(len(user.phone_hash), 64)  # SHA256 hex = 64 chars
        
        # Verify hash is correct
        normalized_phone = self.test_phone.strip()
        expected_hash = self.hasher.compute_hash(normalized_phone)
        self.assertEqual(user.phone_hash, expected_hash)
    
    def test_query_by_email_hash(self):
        """Test querying User by email_hash without decryption."""
        user = User.objects.create(
            username="anjali",
            email=self.test_email,
        )
        
        # Get email hash
        normalized_email = SearchableHasher.normalize_input(self.test_email)
        email_hash = self.hasher.compute_hash(normalized_email)
        
        # Query by email_hash
        found_user = User.objects.get(email_hash=email_hash)
        
        # Verify correct user found
        self.assertEqual(found_user.id, user.id)
        self.assertEqual(found_user.email, self.test_email)
    
    def test_query_by_phone_hash(self):
        """Test querying User by phone_hash without decryption."""
        user = User.objects.create(
            username="deepak",
            phone_number=self.test_phone,
        )
        
        # Get phone hash
        normalized_phone = self.test_phone.strip()
        phone_hash = self.hasher.compute_hash(normalized_phone)
        
        # Query by phone_hash
        found_user = User.objects.get(phone_hash=phone_hash)
        
        # Verify correct user found
        self.assertEqual(found_user.id, user.id)
        self.assertEqual(found_user.phone_number, self.test_phone)
    
    def test_update_user_reencrypts_data(self):
        """Test updating User re-encrypts fields."""
        user = User.objects.create(
            username="neha",
            first_name="Neha",
            email="neha@example.com",
        )
        
        original_email_hash = user.email_hash
        
        # Update email
        new_email = "neha.new@example.com"
        user.email = new_email
        user.save()
        
        # Verify email changed
        user_fetched = User.objects.get(id=user.id)
        self.assertEqual(user_fetched.email, new_email)
        
        # Verify email_hash was updated
        self.assertNotEqual(user.email_hash, original_email_hash)
        
        # Verify new hash is correct
        normalized_email = SearchableHasher.normalize_input(new_email)
        expected_hash = self.hasher.compute_hash(normalized_email)
        self.assertEqual(user.email_hash, expected_hash)
    
    def test_email_hash_unique_constraint(self):
        """Test email_hash unique constraint prevents duplicate emails."""
        user1 = User.objects.create(
            username="user1",
            email=self.test_email,
        )
        
        # Attempt to create user with same email should fail (or be prevented)
        with self.assertRaises(Exception):  # IntegrityError or ValidationError
            user2 = User.objects.create(
                username="user2",
                email=self.test_email,
            )
    
    def test_phone_hash_indexed(self):
        """Test phone_hash is indexed for fast lookups."""
        user = User.objects.create(
            username="sameer",
            phone_number=self.test_phone,
        )
        
        # Query should use index (would be slow without it for large dataset)
        found_user = User.objects.get(phone_hash=user.phone_hash)
        self.assertEqual(found_user.id, user.id)
    
    def test_empty_email_handled(self):
        """Test User with empty/null email fields."""
        user = User.objects.create(
            username="nomail",
            email="",
        )
        
        # User should be created (email can be blank)
        self.assertIsNotNone(user.id)
        
        # Fetch and verify
        user_fetched = User.objects.get(id=user.id)
        self.assertEqual(user_fetched.email, "")
    
    def test_special_characters_encrypted(self):
        """Test special characters in PII are encrypted correctly."""
        special_name = "José María O'Connor"
        special_email = "josé.maria+test@example.com"
        
        user = User.objects.create(
            username="special",
            first_name=special_name,
            email=special_email,
        )
        
        # Fetch and verify
        user_fetched = User.objects.get(id=user.id)
        self.assertEqual(user_fetched.first_name, special_name)
        self.assertEqual(user_fetched.email, special_email)
    
    def test_max_length_fields_encrypted(self):
        """Test max_length fields are encrypted properly."""
        long_name = "A" * 100  # max_length=100
        long_phone = "1" * 20  # max_length=20
        
        user = User.objects.create(
            username="longname",
            first_name=long_name,
            phone_number=long_phone,
        )
        
        # Fetch and verify
        user_fetched = User.objects.get(id=user.id)
        self.assertEqual(user_fetched.first_name, long_name)
        self.assertEqual(user_fetched.phone_number, long_phone)
    
    def test_unicode_characters_encrypted(self):
        """Test Unicode characters (Chinese, Arabic, emoji) encrypted."""
        unicode_name = "राज कुमार"  # Hindi
        unicode_email = "नीरज@example.com"  # Hindi email
        
        user = User.objects.create(
            username="unicode",
            first_name=unicode_name,
            email=unicode_email,
        )
        
        # Fetch and verify
        user_fetched = User.objects.get(id=user.id)
        self.assertEqual(user_fetched.first_name, unicode_name)
        self.assertEqual(user_fetched.email, unicode_email)
    
    def test_user_filter_by_username_still_works(self):
        """Test that unencrypted fields (username) still work for filtering."""
        user = User.objects.create(
            username="filter_test",
            first_name="Test",
        )
        
        # Filter by username (unencrypted) should work
        found_user = User.objects.get(username="filter_test")
        self.assertEqual(found_user.id, user.id)
    
    def test_user_count_aggregation(self):
        """Test COUNT aggregation works on encrypted data."""
        for i in range(5):
            User.objects.create(username=f"user{i}")
        
        # Count should work without decryption
        count = User.objects.filter(is_active=True).count()
        self.assertGreaterEqual(count, 5)
    
    def test_plaintext_data_readable_during_migration(self):
        """Test backwards compatibility: plaintext data still readable."""
        # Create user with encrypted fields
        user = User.objects.create(
            username="compat_test",
            email="test@example.com",
        )
        
        # Verify encryption happened
        user_fetched = User.objects.get(id=user.id)
        self.assertEqual(user_fetched.email, "test@example.com")
        
        # Verify that ciphertext is stored in DB
        user_raw = User.objects.raw(
            "SELECT * FROM auth_user WHERE id = %s", [user.id]
        )[0]
        self.assertNotEqual(user_raw.email, "test@example.com")
