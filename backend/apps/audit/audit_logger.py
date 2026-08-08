"""
Decryption Audit Logging Module

Provides centralized audit logging for all decryption operations.
Every time sensitive encrypted data is decrypted, a record is logged
for compliance, security investigation, and incident response.

Usage:
    from apps.audit.audit_logger import AuditLogger
    
    # Log successful decryption
    AuditLogger.log_decryption(
        user_id=user.id,
        record_type='User',
        record_id=user.id,
        field_name='first_name',
        result='success',
        ip_address='192.168.1.1',
        user_agent='Mozilla/5.0...',
    )
    
    # Log failure
    AuditLogger.log_decryption(
        user_id=user.id,
        record_type='User',
        record_id=user.id,
        field_name='email',
        result='failure',
        reason='Key version not found',
        ip_address='192.168.1.1',
        user_agent='Mozilla/5.0...',
    )
"""

import logging
from datetime import datetime
from typing import Optional
from django.utils import timezone

from apps.audit.models import DecryptionAuditLog
from apps.core.key_manager import get_key_manager

logger = logging.getLogger(__name__)


class AuditLoggerError(Exception):
    """Raised when audit logging fails."""
    pass


class AuditLogger:
    """
    Centralized audit logging for decryption operations.
    
    Logs all decryption operations to DecryptionAuditLog model
    for compliance, security investigation, and audit trails.
    
    Thread-safe: uses Django ORM which handles concurrency.
    """
    
    @staticmethod
    def log_decryption(
        user_id: Optional[int] = None,
        record_type: str = '',
        record_id: int = 0,
        field_name: str = '',
        result: str = 'success',
        reason: Optional[str] = None,
        ip_address: str = 'unknown',
        user_agent: str = 'unknown',
        request_path: Optional[str] = None,
        service_account: Optional[str] = None,
    ) -> DecryptionAuditLog:
        """
        Log a decryption operation to audit trail.
        
        Called whenever encrypted data is decrypted. Records all metadata
        needed for compliance audits and security investigation.
        
        Args:
            user_id: ID of user who triggered decryption (None for service account)
            record_type: Type of record ('User', 'Patient', 'GPS')
            record_id: ID of record that was decrypted
            field_name: Name of field that was decrypted (e.g., 'first_name')
            result: 'success' or 'failure'
            reason: If failed, reason why (e.g., 'Key unavailable')
            ip_address: Client IP address
            user_agent: Client User-Agent header
            request_path: API endpoint that triggered decryption
            service_account: Name of service account (if not user_id)
            
        Returns:
            DecryptionAuditLog record that was created
            
        Raises:
            AuditLoggerError: If logging fails
            
        Example:
            >>> log = AuditLogger.log_decryption(
            ...     user_id=123,
            ...     record_type='User',
            ...     record_id=123,
            ...     field_name='email',
            ...     result='success',
            ...     ip_address='192.168.1.1',
            ... )
            >>> log.id
            1
        """
        try:
            # Validate record type
            if record_type not in dict(DecryptionAuditLog.RECORD_TYPES):
                raise AuditLoggerError(
                    f"Invalid record_type: {record_type}. "
                    f"Must be one of: {[t[0] for t in DecryptionAuditLog.RECORD_TYPES]}"
                )
            
            # Validate result
            if result not in dict(DecryptionAuditLog.RESULTS):
                raise AuditLoggerError(
                    f"Invalid result: {result}. Must be 'success' or 'failure'"
                )
            
            # Get current key version
            try:
                manager = get_key_manager()
                key_version = manager.get_current_key_version()
            except Exception as e:
                logger.warning(f"Failed to get key version for audit log: {str(e)}")
                key_version = 1
            
            # Create audit log entry
            audit_log = DecryptionAuditLog(
                timestamp=timezone.now(),
                user_id=user_id,
                service_account=service_account,
                record_type=record_type,
                record_id=record_id,
                field_name=field_name,
                result=result,
                reason=reason,
                ip_address=ip_address,
                user_agent=user_agent,
                request_path=request_path,
                key_version=key_version,
            )
            
            # Save to database
            audit_log.save()
            
            # Log to application logger
            if result == 'failure':
                logger.warning(
                    f"Decryption failed for {record_type}/{record_id}.{field_name}: {reason}"
                )
            else:
                logger.debug(
                    f"Decrypted {record_type}/{record_id}.{field_name} for user {user_id}"
                )
            
            return audit_log
        
        except Exception as e:
            logger.error(f"Failed to create decryption audit log: {str(e)}")
            raise AuditLoggerError(f"Failed to log decryption: {str(e)}") from e
    
    @staticmethod
    def log_decryption_success(
        user_id: Optional[int] = None,
        record_type: str = '',
        record_id: int = 0,
        field_name: str = '',
        ip_address: str = 'unknown',
        user_agent: str = 'unknown',
        request_path: Optional[str] = None,
        service_account: Optional[str] = None,
    ) -> DecryptionAuditLog:
        """
        Convenience method to log successful decryption.
        
        Args:
            Same as log_decryption
            
        Returns:
            DecryptionAuditLog record
        """
        return AuditLogger.log_decryption(
            user_id=user_id,
            record_type=record_type,
            record_id=record_id,
            field_name=field_name,
            result='success',
            ip_address=ip_address,
            user_agent=user_agent,
            request_path=request_path,
            service_account=service_account,
        )
    
    @staticmethod
    def log_decryption_failure(
        user_id: Optional[int] = None,
        record_type: str = '',
        record_id: int = 0,
        field_name: str = '',
        reason: str = 'Unknown error',
        ip_address: str = 'unknown',
        user_agent: str = 'unknown',
        request_path: Optional[str] = None,
        service_account: Optional[str] = None,
    ) -> DecryptionAuditLog:
        """
        Convenience method to log failed decryption.
        
        Args:
            Same as log_decryption, with required 'reason'
            
        Returns:
            DecryptionAuditLog record
        """
        return AuditLogger.log_decryption(
            user_id=user_id,
            record_type=record_type,
            record_id=record_id,
            field_name=field_name,
            result='failure',
            reason=reason,
            ip_address=ip_address,
            user_agent=user_agent,
            request_path=request_path,
            service_account=service_account,
        )
    
    @staticmethod
    def get_decryption_logs(
        user_id: Optional[int] = None,
        record_type: Optional[str] = None,
        record_id: Optional[int] = None,
        days: int = 7,
    ):
        """
        Retrieve decryption logs for audit purposes.
        
        Args:
            user_id: Filter by user who accessed data
            record_type: Filter by record type ('User', 'Patient', 'GPS')
            record_id: Filter by specific record ID
            days: Look back this many days (default: 7)
            
        Returns:
            QuerySet of DecryptionAuditLog records
            
        Example:
            >>> # Get all decryptions by user 123 in past week
            >>> logs = AuditLogger.get_decryption_logs(user_id=123, days=7)
            >>> for log in logs:
            ...     print(log)
        """
        from django.utils import timezone
        from datetime import timedelta
        
        # Start with all logs from past N days
        cutoff_date = timezone.now() - timedelta(days=days)
        queryset = DecryptionAuditLog.objects.filter(timestamp__gte=cutoff_date)
        
        # Apply optional filters
        if user_id is not None:
            queryset = queryset.filter(user_id=user_id)
        
        if record_type is not None:
            queryset = queryset.filter(record_type=record_type)
        
        if record_id is not None:
            queryset = queryset.filter(record_id=record_id)
        
        return queryset.order_by('-timestamp')
    
    @staticmethod
    def count_failed_decryptions(
        user_id: Optional[int] = None,
        hours: int = 24,
    ) -> int:
        """
        Count failed decryption attempts (security monitoring).
        
        Useful for detecting unauthorized access attempts or
        key management issues.
        
        Args:
            user_id: Filter by user
            hours: Look back this many hours
            
        Returns:
            Number of failed decryption attempts
            
        Example:
            >>> # Count failed decryptions in past hour
            >>> fails = AuditLogger.count_failed_decryptions(hours=1)
            >>> if fails > 10:
            ...     print("Suspicious activity!")
        """
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(hours=hours)
        queryset = DecryptionAuditLog.objects.filter(
            result='failure',
            timestamp__gte=cutoff_date
        )
        
        if user_id is not None:
            queryset = queryset.filter(user_id=user_id)
        
        return queryset.count()
    
    @staticmethod
    def get_top_accessed_records(
        record_type: str,
        limit: int = 10,
        days: int = 30,
    ):
        """
        Get most-accessed records for a given type (compliance reporting).
        
        Args:
            record_type: 'User', 'Patient', or 'GPS'
            limit: Top N records to return
            days: Look back this many days
            
        Returns:
            List of (record_id, access_count) tuples
            
        Example:
            >>> # Get most-accessed patient records
            >>> top = AuditLogger.get_top_accessed_records('Patient', limit=5)
            >>> for record_id, count in top:
            ...     print(f"Patient {record_id}: {count} accesses")
        """
        from django.utils import timezone
        from django.db.models import Count
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        logs = DecryptionAuditLog.objects.filter(
            record_type=record_type,
            timestamp__gte=cutoff_date,
            result='success'
        ).values('record_id').annotate(
            access_count=Count('id')
        ).order_by('-access_count')[:limit]
        
        return [(log['record_id'], log['access_count']) for log in logs]
