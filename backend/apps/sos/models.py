"""SOS/Emergency models"""
from django.db import models
from django.contrib.gis.db import models as gis_models
from apps.core.models import BaseModel, SoftDeleteModel
from apps.auth.models import User


class SosAlert(BaseModel):
    """SOS/Emergency alert"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='sos_alerts')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    latitude = models.FloatField()
    longitude = models.FloatField()
    description = models.TextField(blank=True)
    severity = models.CharField(
        max_length=10,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')],
        default='medium'
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['user', 'status']),
        ]
    
    def __str__(self):
        return f"SOS from {self.user.username} at {self.created_at}"


class DeviceFingerprint(BaseModel):
    """
    Device fingerprint tracking for rate limiting and anomaly detection.
    
    Phase 1.2: Tracks unique device fingerprints for DDoS protection.
    Fingerprints are 64-character hex strings generated on client side
    (SHA256 hash of device identifiers).
    
    Attributes:
        fingerprint: Unique device fingerprint (64-char hex string)
        ip_address: IP address where fingerprint was first seen
        user_agent: User-Agent header
        device_model: Device model (e.g., "iPhone12", "Samsung Galaxy S21")
        app_version: Application version
        os_version: Operating system version
        first_seen: Timestamp when fingerprint was first seen (auto_now_add)
    """
    fingerprint = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        help_text="64-character hex string (SHA256 hash)"
    )
    ip_address = models.GenericIPAddressField(
        db_index=True,
        help_text="IP address where fingerprint was first seen"
    )
    user_agent = models.TextField(blank=True, help_text="User-Agent header")
    device_model = models.CharField(
        max_length=255,
        blank=True,
        help_text="Device model name"
    )
    app_version = models.CharField(
        max_length=20,
        blank=True,
        help_text="App version"
    )
    os_version = models.CharField(
        max_length=50,
        blank=True,
        help_text="OS version"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Device Fingerprint'
        verbose_name_plural = 'Device Fingerprints'
        indexes = [
            models.Index(fields=['fingerprint', 'created_at']),
            models.Index(fields=['ip_address', 'created_at']),
        ]
    
    def __str__(self):
        return f"Fingerprint {self.fingerprint[:16]}... from {self.ip_address}"


class SOSAuditLog(SoftDeleteModel):
    """
    Immutable audit log for all SOS attempts (success and failure).
    
    Phase 1.2: Logs all SOS creation attempts with full context for
    compliance and DDoS attack investigation.
    
    Records:
    - All rate limit check results (IP and device)
    - Geofence validation results
    - Timestamp of attempt
    - Device and network information
    - Final outcome (created, rate_limited, invalid_location, error)
    
    Immutability:
    - Soft delete only (deleted_at set instead of actual delete)
    - Read-only in admin interface
    - No updates allowed after creation
    """
    
    RATE_LIMIT_STATUS_CHOICES = [
        ('PASS', 'Passed'),
        ('REJECT', 'Rejected'),
        ('WARN', 'Warning'),
    ]
    
    GEOFENCE_STATUS_CHOICES = [
        ('PASS', 'Passed'),
        ('REJECT', 'Rejected'),
    ]
    
    RESULT_CHOICES = [
        ('SUCCESS', 'Alert Created'),
        ('RATE_LIMITED_IP', 'Rate Limited (IP)'),
        ('RATE_LIMITED_DEVICE', 'Rate Limited (Device)'),
        ('INVALID_LOCATION', 'Invalid Location'),
        ('INVALID_FINGERPRINT', 'Invalid Fingerprint'),
        ('ERROR', 'Error'),
    ]
    
    # Alert reference
    sos_alert = models.ForeignKey(
        'SosAlert',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='audit_logs',
        help_text="Reference to SOS alert (null if not created)"
    )
    
    # Device information
    device_fingerprint = models.CharField(
        max_length=64,
        db_index=True,
        help_text="Device fingerprint from request"
    )
    device_model = models.CharField(
        max_length=255,
        blank=True,
        help_text="Device model name"
    )
    app_version = models.CharField(
        max_length=20,
        blank=True,
        help_text="App version"
    )
    
    # Network information
    ip_address = models.GenericIPAddressField(
        db_index=True,
        help_text="Client IP address"
    )
    user_agent = models.TextField(
        blank=True,
        help_text="User-Agent header"
    )
    
    # Location information
    latitude = models.FloatField(help_text="GPS latitude")
    longitude = models.FloatField(help_text="GPS longitude")
    radius = models.IntegerField(blank=True, null=True, help_text="Alert radius (meters)")
    
    # DDoS protection checks
    rate_limit_ip_status = models.CharField(
        max_length=20,
        choices=RATE_LIMIT_STATUS_CHOICES,
        default='PASS',
        help_text="IP rate limit check result"
    )
    rate_limit_device_status = models.CharField(
        max_length=20,
        choices=RATE_LIMIT_STATUS_CHOICES,
        default='PASS',
        help_text="Device rate limit check result"
    )
    geofence_status = models.CharField(
        max_length=20,
        choices=GEOFENCE_STATUS_CHOICES,
        default='PASS',
        help_text="Geofence validation result"
    )
    
    # Result and reason
    result = models.CharField(
        max_length=50,
        choices=RESULT_CHOICES,
        db_index=True,
        help_text="Final outcome"
    )
    reason = models.TextField(
        blank=True,
        help_text="Detailed reason for failure (if applicable)"
    )
    
    # User reference
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='sos_audit_logs',
        help_text="Authenticated user (if any)"
    )
    
    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="Attempt timestamp"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'SOS Audit Log'
        verbose_name_plural = 'SOS Audit Logs'
        indexes = [
            models.Index(fields=['created_at', 'result']),
            models.Index(fields=['ip_address', 'created_at']),
            models.Index(fields=['device_fingerprint', 'created_at']),
            models.Index(fields=['result', 'created_at']),
        ]
    
    def __str__(self):
        return (
            f"SOS audit {self.result} - "
            f"{self.device_fingerprint[:12]}... "
            f"from {self.ip_address} at {self.created_at}"
        )
    
    @property
    def is_success(self) -> bool:
        """Check if attempt was successful"""
        return self.result == 'SUCCESS'
    
    @property
    def is_rate_limited(self) -> bool:
        """Check if attempt was rate limited"""
        return 'RATE_LIMITED' in self.result
    
    @property
    def is_geofence_violation(self) -> bool:
        """Check if attempt violated geofence"""
        return self.result == 'INVALID_LOCATION'


class SosLog(BaseModel):
    """Audit log for all SOS activities (Phase 1.5)"""
    alert = models.ForeignKey(SosAlert, on_delete=models.PROTECT, related_name='logs')
    action = models.CharField(max_length=50)
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    details = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-created_at']


# Placeholder URLs
urlpatterns = []
