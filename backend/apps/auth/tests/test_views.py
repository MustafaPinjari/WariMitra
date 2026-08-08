"""
Integration Tests for Authentication Views
Phase 1.1 Implementation: JWT Token Invalidation & Revocation System
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from apps.auth.redis_manager import token_blacklist
import json

User = get_user_model()


class JWTTokenObtainTests(APITestCase):
    """Test JWT token obtain endpoint"""
    
    def setUp(self):
        """Setup test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='pilgrim'
        )
        self.url = reverse('auth:token_obtain_pair')
    
    def test_obtain_token_success(self):
        """Test successful token obtain"""
        response = self.client.post(self.url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        
        # Verify user data is included
        self.assertEqual(response.data['user']['username'], 'testuser')
    
    def test_obtain_token_invalid_credentials(self):
        """Test token obtain with invalid credentials"""
        response = self.client.post(self.url, {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        
        self.assertEqual(response.status_code, 401)


class LogoutViewTests(APITestCase):
    """Test user logout endpoint"""
    
    def setUp(self):
        """Setup test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Get JWT token
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
        self.logout_url = reverse('auth:logout')
    
    def test_logout_success(self):
        """Test successful logout"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.post(self.logout_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.data)
    
    def test_logout_revokes_token(self):
        """Test that logout actually revokes the token"""
        if not token_blacklist.is_connected:
            self.skipTest("Redis not available")
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.post(self.logout_url)
        
        self.assertEqual(response.status_code, 200)
        
        # Verify token is blacklisted
        is_blacklisted = token_blacklist.is_blacklisted(self.access_token)
        self.assertTrue(is_blacklisted, "Token should be blacklisted after logout")
    
    def test_logout_requires_authentication(self):
        """Test that logout requires authenticated user"""
        response = self.client.post(self.logout_url)
        
        # Should be rejected by IsAuthenticated permission
        self.assertEqual(response.status_code, 401)
    
    def test_logout_without_bearer_token(self):
        """Test logout without Bearer token in header"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid')
        response = self.client.post(self.logout_url)
        
        # Should fail due to invalid token format
        self.assertIn(response.status_code, [400, 401])
    
    def test_logout_prevents_token_reuse(self):
        """Test that revoked token cannot be used again"""
        if not token_blacklist.is_connected:
            self.skipTest("Redis not available")
        
        # Logout
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, 200)
        
        # Try to use token again for another request
        # Create a test endpoint that requires authentication
        test_url = '/api/v1/auth/logout/'  # Using logout as test endpoint
        
        response = self.client.post(test_url)
        # Should be blocked by TokenBlacklistMiddleware
        self.assertEqual(response.status_code, 401)
        self.assertIn('revoked', response.data.get('error', '').lower())


class RevokeAllUserTokensViewTests(APITestCase):
    """Test admin endpoint to revoke all user tokens"""
    
    def setUp(self):
        """Setup test data"""
        self.client = APIClient()
        
        # Create admin user
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_staff=True,
            is_superuser=True
        )
        
        # Create regular user
        self.target_user = User.objects.create_user(
            username='targetuser',
            email='target@example.com',
            password='targetpass123'
        )
        
        # Get admin JWT token
        admin_refresh = RefreshToken.for_user(self.admin)
        self.admin_token = str(admin_refresh.access_token)
        
        # Get target user's JWT token
        target_refresh = RefreshToken.for_user(self.target_user)
        self.target_token = str(target_refresh.access_token)
        
        self.revoke_url = reverse(
            'auth:revoke_tokens',
            kwargs={'user_id': self.target_user.id}
        )
    
    def test_revoke_tokens_success(self):
        """Test successful token revocation"""
        if not token_blacklist.is_connected:
            self.skipTest("Redis not available")
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.post(self.revoke_url, {
            'reason': 'admin_revoke'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['user_id'], self.target_user.id)
    
    def test_revoke_tokens_requires_admin(self):
        """Test that only admins can revoke tokens"""
        # Non-admin user
        regular_user = User.objects.create_user(
            username='regularuser',
            email='regular@example.com',
            password='regularpass123'
        )
        regular_refresh = RefreshToken.for_user(regular_user)
        regular_token = str(regular_refresh.access_token)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {regular_token}')
        response = self.client.post(self.revoke_url, {
            'reason': 'admin_revoke'
        })
        
        # Should be forbidden due to IsAdminUser permission
        self.assertEqual(response.status_code, 403)
    
    def test_revoke_tokens_nonexistent_user(self):
        """Test revoking tokens for non-existent user"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        
        fake_url = reverse(
            'auth:revoke_tokens',
            kwargs={'user_id': 99999}
        )
        response = self.client.post(fake_url, {
            'reason': 'admin_revoke'
        })
        
        self.assertEqual(response.status_code, 404)
    
    def test_revoke_tokens_invalid_reason(self):
        """Test revocation with invalid reason"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.post(self.revoke_url, {
            'reason': 'invalid_reason'
        })
        
        self.assertEqual(response.status_code, 400)
    
    def test_revoke_tokens_all_reasons(self):
        """Test all valid revocation reasons"""
        valid_reasons = ['logout', 'admin_revoke', 'password_reset', 'security_incident', 'device_lost']
        
        for reason in valid_reasons:
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
            response = self.client.post(self.revoke_url, {
                'reason': reason
            })
            
            self.assertEqual(response.status_code, 200, f"Should accept reason: {reason}")
    
    def test_revoke_tokens_blocks_future_use(self):
        """Test that revoked tokens cannot be used afterward"""
        if not token_blacklist.is_connected:
            self.skipTest("Redis not available")
        
        # Revoke all target user's tokens
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.post(self.revoke_url, {
            'reason': 'admin_revoke'
        })
        self.assertEqual(response.status_code, 200)
        
        # Try to use target user's token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.target_token}')
        response = self.client.post('/api/v1/auth/logout/')
        
        # Should be blocked
        self.assertEqual(response.status_code, 401)


class TokenBlacklistMiddlewareTests(APITestCase):
    """Test TokenBlacklistMiddleware integration"""
    
    def setUp(self):
        """Setup test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
    
    def test_middleware_allows_valid_token(self):
        """Test that middleware allows valid tokens"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.post(reverse('auth:logout'))
        
        # Should reach the logout view (not blocked by middleware)
        self.assertEqual(response.status_code, 200)
    
    def test_middleware_blocks_blacklisted_token(self):
        """Test that middleware blocks blacklisted tokens"""
        if not token_blacklist.is_connected:
            self.skipTest("Redis not available")
        
        # Blacklist the token manually
        token_blacklist.add_to_blacklist(
            token=self.access_token,
            user_id=self.user.id,
            reason='logout'
        )
        
        # Try to use blacklisted token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.post(reverse('auth:logout'))
        
        # Should be blocked by middleware
        self.assertEqual(response.status_code, 401)
        self.assertIn('revoked', response.data.get('error', '').lower())
    
    def test_middleware_ignores_requests_without_token(self):
        """Test that middleware doesn't interfere with unauthenticated requests"""
        # Request without authentication should be handled by permission classes
        response = self.client.post(reverse('auth:logout'))
        
        # Should be rejected by IsAuthenticated, not blocked by middleware
        self.assertEqual(response.status_code, 401)


class AuditTrailTests(APITestCase):
    """Test audit trail generation"""
    
    def setUp(self):
        """Setup test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_staff=True
        )
        
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
        admin_refresh = RefreshToken.for_user(self.admin)
        self.admin_token = str(admin_refresh.access_token)
    
    def test_logout_creates_audit_entry(self):
        """Test that logout creates audit log entry"""
        from apps.auth.models import TokenRevocation
        
        initial_count = TokenRevocation.objects.count()
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        self.client.post(reverse('auth:logout'))
        
        final_count = TokenRevocation.objects.count()
        self.assertEqual(final_count, initial_count + 1)
    
    def test_admin_revoke_creates_audit_entry(self):
        """Test that admin revocation creates audit log entry"""
        from apps.auth.models import TokenRevocation
        
        initial_count = TokenRevocation.objects.count()
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        url = reverse('auth:revoke_tokens', kwargs={'user_id': self.user.id})
        self.client.post(url, {'reason': 'admin_revoke'})
        
        final_count = TokenRevocation.objects.count()
        self.assertGreater(final_count, initial_count)
        
        # Verify audit entry includes admin ID
        latest_log = TokenRevocation.objects.latest('created_at')
        self.assertEqual(latest_log.revoked_by_id, self.admin.id)
