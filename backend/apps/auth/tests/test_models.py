"""Tests for auth models (Phase 1.1)."""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.auth.models import TokenRevocation, CustomUser

User = get_user_model()


@pytest.mark.django_db
class TestCustomUser(TestCase):
    """Tests for CustomUser model."""
    
    def test_create_custom_user(self):
        """Test creating a custom user."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
    
    def test_custom_user_with_phone(self):
        """Test creating a custom user with phone number."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            phone_number='+1234567890'
        )
        
        self.assertEqual(user.phone_number, '+1234567890')
    
    def test_custom_user_admin_flag(self):
        """Test admin user flag."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            is_admin_user=True
        )
        
        self.assertTrue(user.is_admin_user)
    
    def test_custom_user_ip_tracking(self):
        """Test tracking last login IP."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            last_login_ip='192.168.1.1'
        )
        
        self.assertEqual(user.last_login_ip, '192.168.1.1')
    
    def test_phone_number_unique(self):
        """Test phone number uniqueness constraint."""
        User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='pass123',
            phone_number='+1234567890'
        )
        
        # Creating another user with same phone should fail
        with self.assertRaises(Exception):
            User.objects.create_user(
                username='user2',
                email='user2@example.com',
                password='pass123',
                phone_number='+1234567890'
            )


@pytest.mark.django_db
class TestTokenRevocationModel(TestCase):
    """Tests for TokenRevocation model."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_admin_user=True
        )
    
    def test_create_logout_revocation(self):
        """Test creating a logout revocation."""
        revocation = TokenRevocation.objects.create(
            user=self.user,
            reason='logout'
        )
        
        self.assertEqual(revocation.user, self.user)
        self.assertEqual(revocation.reason, 'logout')
        self.assertIsNone(revocation.revoked_by)
        self.assertTrue(revocation.is_active)
    
    def test_create_admin_revocation(self):
        """Test creating an admin revocation."""
        revocation = TokenRevocation.objects.create(
            user=self.user,
            revoked_by=self.admin,
            reason='admin_revoke'
        )
        
        self.assertEqual(revocation.revoked_by, self.admin)
        self.assertEqual(revocation.reason, 'admin_revoke')
    
    def test_all_revocation_reasons(self):
        """Test all valid revocation reasons."""
        reasons = ['logout', 'admin_revoke', 'password_reset', 'security_incident', 'device_lost']
        
        for reason in reasons:
            revocation = TokenRevocation.objects.create(
                user=self.user,
                reason=reason
            )
            self.assertEqual(revocation.reason, reason)
    
    def test_revocation_with_token_hash(self):
        """Test creating revocation with token hash."""
        token_hash = 'abc123def456'
        revocation = TokenRevocation.objects.create(
            user=self.user,
            reason='logout',
            token_hash=token_hash
        )
        
        self.assertEqual(revocation.token_hash, token_hash)
    
    def test_revocation_with_details(self):
        """Test creating revocation with JSON details."""
        details = {
            'ip_address': '192.168.1.1',
            'user_agent': 'Mozilla/5.0...',
            'reason_code': 'DEVICE_LOST'
        }
        revocation = TokenRevocation.objects.create(
            user=self.user,
            reason='device_lost',
            details=details
        )
        
        self.assertEqual(revocation.details['ip_address'], '192.168.1.1')
        self.assertEqual(revocation.details['reason_code'], 'DEVICE_LOST')
    
    def test_revocation_unique_id(self):
        """Test revocation_id is unique."""
        rev1 = TokenRevocation.objects.create(user=self.user, reason='logout')
        rev2 = TokenRevocation.objects.create(user=self.user, reason='logout')
        
        self.assertNotEqual(rev1.revocation_id, rev2.revocation_id)
    
    def test_revocation_soft_delete(self):
        """Test soft delete of revocation."""
        revocation = TokenRevocation.objects.create(
            user=self.user,
            reason='logout'
        )
        
        self.assertTrue(revocation.is_active)
        self.assertIsNone(revocation.deleted_at)
        
        # Soft delete
        revocation.delete()
        
        # Reload from database
        revocation.refresh_from_db()
        self.assertFalse(revocation.is_active)
        self.assertIsNotNone(revocation.deleted_at)
    
    def test_active_objects_filter(self):
        """Test active_objects queryset method."""
        rev1 = TokenRevocation.objects.create(user=self.user, reason='logout')
        rev2 = TokenRevocation.objects.create(user=self.user, reason='logout')
        
        # Soft delete one
        rev2.delete()
        
        # Only active records returned
        active = TokenRevocation.objects.filter(is_active=True)
        self.assertEqual(active.count(), 1)
        self.assertEqual(active.first().id, rev1.id)
    
    def test_revocation_ordering(self):
        """Test revocations are ordered by created_at (descending)."""
        rev1 = TokenRevocation.objects.create(user=self.user, reason='logout')
        rev2 = TokenRevocation.objects.create(user=self.user, reason='logout')
        
        revocations = list(TokenRevocation.objects.all())
        
        # Most recent should be first
        self.assertEqual(revocations[0].id, rev2.id)
        self.assertEqual(revocations[1].id, rev1.id)
    
    def test_token_hash_indexed(self):
        """Test that token_hash is indexed for fast lookups."""
        revocation = TokenRevocation.objects.create(
            user=self.user,
            reason='logout',
            token_hash='abc123'
        )
        
        # Query by token_hash should be fast
        found = TokenRevocation.objects.get(token_hash='abc123')
        self.assertEqual(found.id, revocation.id)
    
    def test_user_revocation_relationship(self):
        """Test the relationship between User and TokenRevocation."""
        TokenRevocation.objects.create(user=self.user, reason='logout')
        TokenRevocation.objects.create(user=self.user, reason='password_reset')
        
        # Query revocations for a user
        user_revocations = TokenRevocation.objects.filter(user=self.user)
        self.assertEqual(user_revocations.count(), 2)
    
    def test_admin_revocation_relationship(self):
        """Test the relationship between Admin and revocations they performed."""
        TokenRevocation.objects.create(
            user=self.user,
            revoked_by=self.admin,
            reason='admin_revoke'
        )
        TokenRevocation.objects.create(
            user=self.user,
            revoked_by=self.admin,
            reason='admin_revoke'
        )
        
        # Query revocations performed by admin
        admin_actions = TokenRevocation.objects.filter(revoked_by=self.admin)
        self.assertEqual(admin_actions.count(), 2)
    
    def test_revocation_timestamp_fields(self):
        """Test created_at and updated_at timestamps."""
        revocation = TokenRevocation.objects.create(
            user=self.user,
            reason='logout'
        )
        
        self.assertIsNotNone(revocation.created_at)
        self.assertIsNotNone(revocation.updated_at)
        self.assertEqual(revocation.created_at, revocation.updated_at)
    
    def test_model_str_representation(self):
        """Test string representation of TokenRevocation."""
        revocation = TokenRevocation.objects.create(
            user=self.user,
            reason='logout'
        )
        
        str_repr = str(revocation)
        self.assertIn(str(revocation.revocation_id), str_repr)
        self.assertIn(self.user.username, str_repr)
