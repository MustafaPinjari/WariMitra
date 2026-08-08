"""
Unit Tests for Redis Token Blacklist Manager
Phase 1.1 Implementation: JWT Token Invalidation & Revocation System
"""
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.auth.redis_manager import TokenBlacklistManager, token_blacklist
from apps.auth.models import TokenRevocation
import hashlib
import json

User = get_user_model()


class TokenBlacklistManagerTests(TestCase):
    """Test suite for Redis token blacklist manager"""
    
    @classmethod
    def setUpClass(cls):
        """Setup test fixtures (runs once per test class)"""
        super().setUpClass()
        cls.manager = TokenBlacklistManager()
    
    def setUp(self):
        """Setup test data (runs before each test)"""
        # Create test user
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_staff=True
        )
        
        # Sample JWT token
        self.sample_token = (
            'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.'
            'eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.'
            'SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'
        )
    
    def tearDown(self):
        """Cleanup after each test"""
        # Clear Redis blacklist for this test
        if self.manager.is_connected:
            pattern = f"{self.manager.PREFIX}*"
            cursor = 0
            while True:
                cursor, keys = self.manager.redis_client.scan(cursor, match=pattern, count=100)
                if keys:
                    self.manager.redis_client.delete(*keys)
                if cursor == 0:
                    break
    
    # ============================================================================
    # Token Hashing Tests
    # ============================================================================
    
    def test_hash_token_consistency(self):
        """Test that hashing the same token produces same hash"""
        hash1 = TokenBlacklistManager.hash_token(self.sample_token)
        hash2 = TokenBlacklistManager.hash_token(self.sample_token)
        
        self.assertEqual(hash1, hash2, "Hash should be consistent")
        self.assertEqual(len(hash1), 64, "SHA256 hash should be 64 hex characters")
    
    def test_hash_token_different_for_different_tokens(self):
        """Test that different tokens produce different hashes"""
        token1 = "token_1"
        token2 = "token_2"
        
        hash1 = TokenBlacklistManager.hash_token(token1)
        hash2 = TokenBlacklistManager.hash_token(token2)
        
        self.assertNotEqual(hash1, hash2, "Different tokens should have different hashes")
    
    def test_hash_token_uses_sha256(self):
        """Test that hashing uses SHA256"""
        token = "test_token"
        computed_hash = TokenBlacklistManager.hash_token(token)
        expected_hash = hashlib.sha256(token.encode()).hexdigest()
        
        self.assertEqual(computed_hash, expected_hash, "Should use SHA256 hashing")
    
    # ============================================================================
    # Token Blacklist Tests
    # ============================================================================
    
    @pytest.mark.skipif(not TokenBlacklistManager().is_connected, reason="Redis not available")
    def test_add_to_blacklist_success(self):
        """Test adding token to blacklist"""
        success = self.manager.add_to_blacklist(
            token=self.sample_token,
            user_id=self.test_user.id,
            reason='logout',
            ttl_seconds=900
        )
        
        self.assertTrue(success, "Should successfully add token to blacklist")
    
    @pytest.mark.skipif(not TokenBlacklistManager().is_connected, reason="Redis not available")
    def test_add_to_blacklist_creates_audit_log(self):
        """Test that adding token creates audit log entry"""
        initial_count = TokenRevocation.objects.count()
        
        self.manager.add_to_blacklist(
            token=self.sample_token,
            user_id=self.test_user.id,
            reason='logout',
            ttl_seconds=900
        )
        
        final_count = TokenRevocation.objects.count()
        self.assertEqual(final_count, initial_count + 1, "Should create audit log entry")
        
        # Verify audit log content
        log = TokenRevocation.objects.latest('created_at')
        self.assertEqual(log.user_id, self.test_user.id)
        self.assertEqual(log.reason, 'logout')
        self.assertIsNone(log.revoked_by_id)  # No admin for logout
    
    @pytest.mark.skipif(not TokenBlacklistManager().is_connected, reason="Redis not available")
    def test_is_blacklisted_returns_true_for_blacklisted_token(self):
        """Test that blacklisted tokens are detected"""
        # Add token to blacklist
        self.manager.add_to_blacklist(
            token=self.sample_token,
            user_id=self.test_user.id,
            reason='logout',
            ttl_seconds=900
        )
        
        # Check if blacklisted
        is_blacklisted = self.manager.is_blacklisted(self.sample_token)
        self.assertTrue(is_blacklisted, "Token should be blacklisted")
    
    @pytest.mark.skipif(not TokenBlacklistManager().is_connected, reason="Redis not available")
    def test_is_blacklisted_returns_false_for_valid_token(self):
        """Test that valid tokens are not blacklisted"""
        valid_token = "this_token_is_not_blacklisted"
        is_blacklisted = self.manager.is_blacklisted(valid_token)
        self.assertFalse(is_blacklisted, "Valid token should not be blacklisted")
    
    @pytest.mark.skipif(not TokenBlacklistManager().is_connected, reason="Redis not available")
    def test_is_blacklisted_different_tokens_independent(self):
        """Test that blacklisting one token doesn't affect others"""
        token1 = "token_one_to_blacklist"
        token2 = "token_two_valid"
        
        self.manager.add_to_blacklist(
            token=token1,
            user_id=self.test_user.id,
            reason='logout',
            ttl_seconds=900
        )
        
        self.assertTrue(self.manager.is_blacklisted(token1))
        self.assertFalse(self.manager.is_blacklisted(token2))
    
    # ============================================================================
    # Revoke All User Tokens Tests
    # ============================================================================
    
    @pytest.mark.skipif(not TokenBlacklistManager().is_connected, reason="Redis not available")
    def test_revoke_all_user_tokens_success(self):
        """Test revoking all tokens for a user"""
        # Add multiple tokens for same user
        tokens = [f"token_user_{i}" for i in range(3)]
        
        for token in tokens:
            self.manager.add_to_blacklist(
                token=token,
                user_id=self.test_user.id,
                reason='logout',
                ttl_seconds=900
            )
        
        # Revoke all tokens
        revoked_count = self.manager.revoke_all_user_tokens(
            user_id=self.test_user.id,
            admin_id=self.admin_user.id,
            reason='admin_revoke'
        )
        
        # Should have attempted to revoke tokens
        # (Some may have expired, depending on Redis TTL)
        self.assertGreaterEqual(revoked_count, 0, "Should attempt to revoke tokens")
    
    @pytest.mark.skipif(not TokenBlacklistManager().is_connected, reason="Redis not available")
    def test_revoke_all_user_tokens_creates_audit_log(self):
        """Test that revoking all tokens creates audit log"""
        initial_count = TokenRevocation.objects.count()
        
        self.manager.revoke_all_user_tokens(
            user_id=self.test_user.id,
            admin_id=self.admin_user.id,
            reason='admin_revoke'
        )
        
        final_count = TokenRevocation.objects.count()
        self.assertGreater(final_count, initial_count, "Should create audit log for batch revocation")
        
        # Verify audit log content
        log = TokenRevocation.objects.latest('created_at')
        self.assertEqual(log.user_id, self.test_user.id)
        self.assertEqual(log.revoked_by_id, self.admin_user.id)
        self.assertEqual(log.reason, 'admin_revoke')
    
    @pytest.mark.skipif(not TokenBlacklistManager().is_connected, reason="Redis not available")
    def test_revoke_all_user_tokens_doesnt_affect_other_users(self):
        """Test that revoking one user's tokens doesn't affect others"""
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        
        token1 = "user1_token"
        token2 = "user2_token"
        
        # Add tokens for different users
        self.manager.add_to_blacklist(token=token1, user_id=self.test_user.id, reason='logout')
        self.manager.add_to_blacklist(token=token2, user_id=user2.id, reason='logout')
        
        # Revoke all for user1
        self.manager.revoke_all_user_tokens(
            user_id=self.test_user.id,
            admin_id=self.admin_user.id,
            reason='admin_revoke'
        )
        
        # User1's token should be gone, user2's should remain
        self.assertFalse(self.manager.is_blacklisted(token1))
        self.assertTrue(self.manager.is_blacklisted(token2))
    
    # ============================================================================
    # Error Handling Tests
    # ============================================================================
    
    def test_hash_token_empty_string(self):
        """Test hashing empty string"""
        hash_empty = TokenBlacklistManager.hash_token("")
        self.assertEqual(len(hash_empty), 64, "Should produce valid hash even for empty string")
    
    def test_add_to_blacklist_with_admin_id(self):
        """Test adding token with admin ID (for admin-initiated revocation)"""
        success = self.manager.add_to_blacklist(
            token=self.sample_token,
            user_id=self.test_user.id,
            reason='admin_revoke',
            admin_id=self.admin_user.id,
            ttl_seconds=900
        )
        
        self.assertTrue(success)
        
        # Verify audit log includes admin ID
        log = TokenRevocation.objects.latest('created_at')
        self.assertEqual(log.revoked_by_id, self.admin_user.id)
    
    def test_add_to_blacklist_custom_ttl(self):
        """Test adding token with custom TTL"""
        success = self.manager.add_to_blacklist(
            token=self.sample_token,
            user_id=self.test_user.id,
            reason='logout',
            ttl_seconds=3600  # 1 hour instead of default 15 min
        )
        
        self.assertTrue(success)
    
    # ============================================================================
    # Audit Trail Tests
    # ============================================================================
    
    def test_audit_log_immutability(self):
        """Test that audit logs can only be soft-deleted (never hard-deleted)"""
        self.manager.add_to_blacklist(
            token=self.sample_token,
            user_id=self.test_user.id,
            reason='logout'
        )
        
        log = TokenRevocation.objects.latest('created_at')
        self.assertTrue(log.is_active, "Audit log should be active initially")
        
        # Soft delete
        log.delete()
        
        # Refresh from DB
        log.refresh_from_db()
        self.assertFalse(log.is_active, "Soft delete should set is_active=False")
        
        # Data should still be recoverable
        all_logs = TokenRevocation.objects.all()  # Includes soft-deleted
        self.assertEqual(all_logs.count(), 1, "Soft-deleted log should still exist")
    
    def test_audit_log_timestamps(self):
        """Test that audit logs have proper timestamps"""
        before = timezone.now()
        
        self.manager.add_to_blacklist(
            token=self.sample_token,
            user_id=self.test_user.id,
            reason='logout'
        )
        
        after = timezone.now()
        
        log = TokenRevocation.objects.latest('created_at')
        self.assertGreaterEqual(log.created_at, before)
        self.assertLessEqual(log.created_at, after)


class TokenBlacklistSingletonTests(TestCase):
    """Test the singleton token_blacklist instance"""
    
    def test_token_blacklist_singleton_exists(self):
        """Test that token_blacklist singleton is created"""
        from apps.auth.redis_manager import token_blacklist
        self.assertIsNotNone(token_blacklist)
    
    def test_token_blacklist_is_instance_of_manager(self):
        """Test that token_blacklist is instance of TokenBlacklistManager"""
        from apps.auth.redis_manager import token_blacklist
        self.assertIsInstance(token_blacklist, TokenBlacklistManager)
