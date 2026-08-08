"""Audit models - Phase 1.3: Decryption audit logging"""
from django.db import models
from django.core.exceptions import ValidationError
from apps.core.models import BaseModel
from apps.auth.models import User


class AuditLog(BaseModel):
    """Immutable audit trail of all critical actions"""
    ACTION_TYPES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('revoke', 'Token Revoke'),
        ('login', 'Login'),
        ('logout', 'Logout'),
    ]
    
    action = models.CharField(max_length=50, choices=ACTION_TYPES)
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=36)
    changes = models.JSONField(default=dict, blank=True)
    details = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['action', 'created_at']),
            models.Index(fields=['actor', 'created_at']),
            models.Index(fields=['model_name', 'object_id']),
        ]
    
    def __str__(self):
        return f"{self.action} on {self.model_name} by {self.actor}"


class DecryptionAuditLog(BaseModel):
    """
    Immutable, tamper-proof audit log for all decryption operations.
    
    Records every time sensitive encrypted data is decrypted. This enables:
    - Compliance audits: Who accessed what patient/user data
    - Security investigation: Detect unauthorized access patterns
    - Incident response: Determine scope of data exposure
    - Regulatory reporting: GDPR right to know who accessed data
    
    Properties:
    - Immutable: No updates allowed (only INSERT)
    - Indexed: For fast searching by user, record, timestamp
    - Retention: 7+ years (GDPR compliance)
    - No plaintext: Never stores decrypted values, only metadata
    
    Usage:
        DecryptionAuditLog.objects.create(
            timestamp=timezone.now(),
            user_id=user.id,
            record_type='User',
            record_id=user.id,
            field_name='first_name',
            result='success',
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0...',
        )
    """
    
    # Record types that can be decrypted
    RECORD_TYPES = [
        ('User', 'User PII'),
        ('Patient', 'Patient Medical Record'),
        ('GPS', 'GPS Location'),
    ]
    
    # Decryption result
    RESULTS = [
        ('success', 'Successful'),
        ('failure', 'Failed'),
    ]
    
    # Timestamp of decryption (UTC, microsecond precision)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # Who accessed the data
    user_id = models.IntegerField(null=True, blank=True, db_index=True)  # Store as int for flexibility
    service_account = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    
    # What was accessed
    record_type = models.CharField(
        max_length=50,
        choices=RECORD_TYPES,
        db_index=True
    )
    record_id = models.IntegerField(db_index=True)
    field_name = models.CharField(max_length=100)  # e.g., 'first_name', 'condition'
    
    # Result of decryption
    result = models.CharField(
        max_length=20,
        choices=RESULTS,
        db_index=True
    )
    reason = models.CharField(
        max_length=500,
        null=True,
        blank=True
    )  # Why if failed (e.g., "Key unavailable", "Invalid format")
    
    # Context of access
    ip_address = models.CharField(max_length=50, default='unknown')
    user_agent = models.TextField(default='unknown')
    request_path = models.CharField(max_length=500, null=True, blank=True)
    
    # Encryption metadata
    key_version = models.IntegerField(default=1)  # Which key was used
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['user_id']),
            models.Index(fields=['record_id']),
            models.Index(fields=['record_type', 'record_id']),
            models.Index(fields=['user_id', 'timestamp']),
            models.Index(fields=['result', 'timestamp']),
        ]
        # Prevent bulk updates/deletes (immutability)
        constraints = [
            models.CheckConstraint(
                check=models.Q(timestamp__isnull=False),
                name='decryption_audit_timestamp_not_null'
            ),
        ]
    
    def save(self, *args, **kwargs):
        """
        Override save to enforce immutability.
        Only allow INSERT, no UPDATE.
        """
        if self.pk:
            # Already exists - prevent update
            raise ValidationError(
                "Decryption audit logs are immutable. Cannot update existing records."
            )
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """
        Override delete to prevent deletion.
        """
        raise ValidationError(
            "Decryption audit logs are immutable. Cannot delete records."
        )
    
    def __str__(self):
        return (
            f"Decryption: {self.record_type}/{self.record_id}.{self.field_name} "
            f"by user {self.user_id} at {self.timestamp} ({self.result})"
        )
