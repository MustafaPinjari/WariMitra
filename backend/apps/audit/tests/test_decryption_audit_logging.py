"""
Tests for Phase 1.3 Decryption Audit Logging

Tests cover:
- Logging successful decryption
- Logging failed decryption
- Immutable audit logs (no updates/deletes)
- Querying audit logs by user/record/time
- Admin interface read-only access
"""

import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from apps.audit.models import DecryptionAuditLog
from apps.audit.audit_logger import AuditLogger, AuditLoggerError
from apps.auth.models import User


class DecryptionAuditLogTestCase(TestCase):
    """Test DecryptionAuditLog model functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.user = User.objects.create(
            username="audit_user",
            email="audit@example.com"
        )
    
    def test_create_audit_log_success(self):
        """Test creating a successful decryption audit log."""
        log = DecryptionAuditLog.objects.create(
            user_id=self.user.id,
            record_type='User',
            record_id=self.user.id,
            field_name='email',
            result='success',
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0',
        )
        
        # Verify log was created
        self.assertIsNotNone(log.id)
        self.assertEqual(log.user_id, self.user.id)
        self.assertEqual(log.record_type, 'User')
        self.assertEqual(log.result, 'success')
    
    def test_create_audit_log_failure(self):
        """Test creating a failed decryption audit log."""
        reason = "Encryption key not found for version 2"
        
        log = DecryptionAuditLog.objects.create(
            user_id=self.user.id,
            record_type='Patient',
            record_id=123,
            field_name='condition',
            result='failure',
            reason=reason,
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0',
        )
        
        # Verify log was created with failure info
        self.assertEqual(log.result, 'failure')
        self.assertEqual(log.reason, reason)
    
    def test_audit_log_immutable_no_update(self):
        """Test that audit logs cannot be updated (immutable)."""
        log = DecryptionAuditLog.objects.create(
            user_id=self.user.id,
            record_type='User',
            record_id=self.user.id,
            field_name='email',
            result='success',
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0',
        )
        
        # Attempt to update should fail
        log.result = 'failure'
        
        with self.assertRaises(ValidationError):
            log.save()
    
    def test_audit_log_immutable_no_delete(self):
        """Test that audit logs cannot be deleted (immutable)."""
        log = DecryptionAuditLog.objects.create(
            user_id=self.user.id,
            record_type='User',
            record_id=self.user.id,
            field_name='email',
            result='success',
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0',
        )
        
        # Attempt to delete should fail
        with self.assertRaises(ValidationError):
            log.delete()
    
    def test_audit_logger_log_decryption_success(self):
        """Test AuditLogger.log_decryption_success convenience method."""
        log = AuditLogger.log_decryption_success(
            user_id=self.user.id,
            record_type='User',
            record_id=self.user.id,
            field_name='first_name',
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0',
        )
        
        # Verify log created correctly
        self.assertEqual(log.user_id, self.user.id)
        self.assertEqual(log.result, 'success')
        self.assertIsNone(log.reason)
    
    def test_audit_logger_log_decryption_failure(self):
        """Test AuditLogger.log_decryption_failure convenience method."""
        log = AuditLogger.log_decryption_failure(
            user_id=self.user.id,
            record_type='Patient',
            record_id=456,
            field_name='age',
            reason='Key version mismatch',
            ip_address='192.168.1.2',
            user_agent='Chrome/90',
        )
        
        # Verify log created correctly
        self.assertEqual(log.user_id, self.user.id)
        self.assertEqual(log.result, 'failure')
        self.assertEqual(log.reason, 'Key version mismatch')
    
    def test_query_logs_by_user(self):
        """Test querying audit logs by user."""
        # Create logs for different users
        user2 = User.objects.create(
            username="audit_user2",
            email="audit2@example.com"
        )
        
        for _ in range(3):
            AuditLogger.log_decryption_success(
                user_id=self.user.id,
                record_type='User',
                record_id=self.user.id,
                field_name='email',
            )
        
        for _ in range(2):
            AuditLogger.log_decryption_success(
                user_id=user2.id,
                record_type='User',
                record_id=user2.id,
                field_name='email',
            )
        
        # Query logs for user1
        user1_logs = AuditLogger.get_decryption_logs(user_id=self.user.id, days=7)
        self.assertEqual(user1_logs.count(), 3)
        
        # Query logs for user2
        user2_logs = AuditLogger.get_decryption_logs(user_id=user2.id, days=7)
        self.assertEqual(user2_logs.count(), 2)
    
    def test_query_logs_by_record_type(self):
        """Test querying audit logs by record type."""
        # Create logs for different record types
        AuditLogger.log_decryption_success(
            user_id=self.user.id,
            record_type='User',
            record_id=1,
            field_name='email',
        )
        
        AuditLogger.log_decryption_success(
            user_id=self.user.id,
            record_type='Patient',
            record_id=2,
            field_name='condition',
        )
        
        AuditLogger.log_decryption_success(
            user_id=self.user.id,
            record_type='GPS',
            record_id=3,
            field_name='latitude',
        )
        
        # Query by record type
        user_logs = AuditLogger.get_decryption_logs(record_type='User', days=7)
        self.assertEqual(user_logs.count(), 1)
        self.assertEqual(user_logs[0].record_type, 'User')
        
        patient_logs = AuditLogger.get_decryption_logs(record_type='Patient', days=7)
        self.assertEqual(patient_logs.count(), 1)
        self.assertEqual(patient_logs[0].record_type, 'Patient')
    
    def test_query_logs_by_record_id(self):
        """Test querying audit logs by specific record ID."""
        # Create logs for different records
        for i in range(3):
            AuditLogger.log_decryption_success(
                user_id=self.user.id,
                record_type='User',
                record_id=i+1,
                field_name='email',
            )
        
        # Query by record_id
        logs = AuditLogger.get_decryption_logs(record_id=2, days=7)
        self.assertEqual(logs.count(), 1)
        self.assertEqual(logs[0].record_id, 2)
    
    def test_count_failed_decryptions(self):
        """Test counting failed decryption attempts."""
        # Create successful logs
        for _ in range(2):
            AuditLogger.log_decryption_success(
                user_id=self.user.id,
                record_type='User',
                record_id=1,
                field_name='email',
            )
        
        # Create failed logs
        for _ in range(3):
            AuditLogger.log_decryption_failure(
                user_id=self.user.id,
                record_type='User',
                record_id=1,
                field_name='email',
                reason='Test failure',
            )
        
        # Count failures
        fail_count = AuditLogger.count_failed_decryptions(hours=1)
        self.assertEqual(fail_count, 3)
        
        # Count failures for specific user
        user_fail_count = AuditLogger.count_failed_decryptions(
            user_id=self.user.id, hours=1
        )
        self.assertEqual(user_fail_count, 3)
    
    def test_get_top_accessed_records(self):
        """Test getting most-accessed records."""
        # Create multiple accesses to same record
        for _ in range(5):
            AuditLogger.log_decryption_success(
                user_id=self.user.id,
                record_type='Patient',
                record_id=1,
                field_name='condition',
            )
        
        # Create fewer accesses to other records
        for _ in range(2):
            AuditLogger.log_decryption_success(
                user_id=self.user.id,
                record_type='Patient',
                record_id=2,
                field_name='condition',
            )
        
        # Get top accessed
        top = AuditLogger.get_top_accessed_records('Patient', limit=2, days=30)
        
        # Record 1 should be first (5 accesses)
        self.assertEqual(len(top), 2)
        self.assertEqual(top[0][0], 1)  # record_id
        self.assertEqual(top[0][1], 5)  # access_count
        self.assertEqual(top[1][0], 2)
        self.assertEqual(top[1][1], 2)
    
    def test_audit_log_timestamps(self):
        """Test audit log timestamps are recorded correctly."""
        before = timezone.now()
        
        log = AuditLogger.log_decryption_success(
            user_id=self.user.id,
            record_type='User',
            record_id=1,
            field_name='email',
        )
        
        after = timezone.now()
        
        # Verify timestamp is within range
        self.assertGreaterEqual(log.timestamp, before)
        self.assertLessEqual(log.timestamp, after)
    
    def test_audit_log_no_plaintext_logged(self):
        """Test that plaintext values are not logged (only metadata)."""
        log = AuditLogger.log_decryption_success(
            user_id=self.user.id,
            record_type='User',
            record_id=self.user.id,
            field_name='email',
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0',
        )
        
        # Verify only metadata is logged
        self.assertEqual(log.record_id, self.user.id)
        self.assertEqual(log.field_name, 'email')
        
        # Plaintext email should NOT be stored
        # (Not in reason, changes, or any other field)
        self.assertIsNone(log.reason)
        self.assertEqual(log.ip_address, '192.168.1.1')
        self.assertEqual(log.user_agent, 'Mozilla/5.0')
    
    def test_service_account_logging(self):
        """Test logging decryptions by service accounts."""
        log = AuditLogger.log_decryption_success(
            service_account='batch_job_worker',
            record_type='User',
            record_id=1,
            field_name='email',
        )
        
        # Verify service account logged
        self.assertEqual(log.service_account, 'batch_job_worker')
        self.assertIsNone(log.user_id)
    
    def test_audit_log_with_request_path(self):
        """Test logging with request path."""
        log = AuditLogger.log_decryption_success(
            user_id=self.user.id,
            record_type='User',
            record_id=1,
            field_name='email',
            request_path='/api/users/1/profile/',
        )
        
        # Verify request path logged
        self.assertEqual(log.request_path, '/api/users/1/profile/')
    
    def test_audit_log_indexes(self):
        """Test that audit log indexes are working (no error on query)."""
        # Create multiple logs
        for i in range(10):
            AuditLogger.log_decryption_success(
                user_id=self.user.id,
                record_type='User',
                record_id=i+1,
                field_name='email',
            )
        
        # Query should be fast (using indexes)
        logs = DecryptionAuditLog.objects.filter(
            user_id=self.user.id,
            timestamp__gte=timezone.now() - timedelta(hours=1)
        ).order_by('-timestamp')
        
        # Should not raise exception
        self.assertEqual(logs.count(), 10)
    
    def test_invalid_record_type_rejected(self):
        """Test that invalid record types are rejected."""
        with self.assertRaises(AuditLoggerError):
            AuditLogger.log_decryption_success(
                user_id=self.user.id,
                record_type='InvalidType',  # Not in RECORD_TYPES
                record_id=1,
                field_name='email',
            )
    
    def test_invalid_result_rejected(self):
        """Test that invalid result values are rejected."""
        with self.assertRaises(AuditLoggerError):
            AuditLogger.log_decryption(
                user_id=self.user.id,
                record_type='User',
                record_id=1,
                field_name='email',
                result='invalid_result',  # Not 'success' or 'failure'
            )
