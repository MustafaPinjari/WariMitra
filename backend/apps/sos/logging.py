"""
Audit Logging Module for SOS Endpoint
Phase 1.2 Implementation: DDoS Protection

Provides centralized logging of all SOS attempts to SOSAuditLog model.
Logs are written synchronously in Phase 1.2, will be converted to async
Celery tasks in Phase 2.1.

Example:
    from apps.sos.logging import log_sos_attempt
    
    log_sos_attempt(
        sos_alert_id=alert.id,
        ip_address="192.168.1.1",
        device_fingerprint="abc123...",
        latitude=28.6139,
        longitude=77.2090,
        radius=1000,
        rate_limit_ip_status="PASS",
        rate_limit_device_status="PASS",
        geofence_status="PASS",
        result="SUCCESS"
    )
"""
import logging
from typing import Optional
from django.utils import timezone
from apps.sos.models import SOSAuditLog

logger = logging.getLogger(__name__)


def log_sos_attempt(
    sos_alert_id: Optional[int],
    ip_address: str,
    device_fingerprint: str,
    latitude: float,
    longitude: float,
    radius: Optional[int],
    rate_limit_ip_status: str,
    rate_limit_device_status: str,
    geofence_status: str,
    result: str,
    reason: Optional[str] = None,
    user_id: Optional[int] = None,
    device_model: Optional[str] = None,
    app_version: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> bool:
    """
    Log a SOS attempt to the audit log.
    
    Creates an immutable audit log entry recording all details of an SOS
    creation attempt including all DDoS protection check results.
    
    Args:
        sos_alert_id: ID of created SOS alert (None if not created)
        ip_address: Client IP address
        device_fingerprint: Device fingerprint from request
        latitude: GPS latitude
        longitude: GPS longitude
        radius: Alert radius in meters
        rate_limit_ip_status: IP rate limit check result (PASS/REJECT/WARN)
        rate_limit_device_status: Device rate limit check result (PASS/REJECT/WARN)
        geofence_status: Geofence validation result (PASS/REJECT)
        result: Final outcome (SUCCESS/RATE_LIMITED_IP/RATE_LIMITED_DEVICE/INVALID_LOCATION/ERROR)
        reason: Detailed reason for failure (optional)
        user_id: Authenticated user ID (optional)
        device_model: Device model name (optional)
        app_version: App version (optional)
        user_agent: User-Agent header (optional)
        
    Returns:
        True if logging successful, False otherwise
        
    Raises:
        No exceptions - errors are logged but not raised
        
    Example:
        >>> success = log_sos_attempt(
        ...     sos_alert_id=123,
        ...     ip_address="192.168.1.1",
        ...     device_fingerprint="abc123def456...",
        ...     latitude=28.6139,
        ...     longitude=77.2090,
        ...     radius=1000,
        ...     rate_limit_ip_status="PASS",
        ...     rate_limit_device_status="PASS",
        ...     geofence_status="PASS",
        ...     result="SUCCESS"
        ... )
        >>> if success:
        ...     print("SOS attempt logged")
    """
    try:
        # Validate required parameters
        if not ip_address or not device_fingerprint:
            logger.error("Missing required parameters for SOS logging")
            return False
        
        # Create audit log entry
        log_entry = SOSAuditLog.objects.create(
            sos_alert_id=sos_alert_id,
            ip_address=ip_address,
            device_fingerprint=device_fingerprint,
            latitude=latitude,
            longitude=longitude,
            radius=radius,
            rate_limit_ip_status=rate_limit_ip_status,
            rate_limit_device_status=rate_limit_device_status,
            geofence_status=geofence_status,
            result=result,
            reason=reason or '',
            user_id=user_id,
            device_model=device_model or '',
            app_version=app_version or '',
            user_agent=user_agent or '',
        )
        
        # Log successful audit entry creation
        logger.info(
            f"SOS attempt logged: {result} - "
            f"IP: {ip_address}, FP: {device_fingerprint[:12]}..., "
            f"Loc: ({latitude:.4f}, {longitude:.4f}), "
            f"Rate Limit IP: {rate_limit_ip_status}, "
            f"Rate Limit Device: {rate_limit_device_status}, "
            f"Geofence: {geofence_status}"
        )
        
        return True
        
    except Exception as e:
        logger.error(
            f"Error logging SOS attempt: {str(e)}",
            exc_info=True,
            extra={
                'ip_address': ip_address,
                'device_fingerprint': device_fingerprint,
                'result': result,
            }
        )
        # Fail gracefully - don't let logging errors crash the request
        return False


def log_rate_limit_exceeded(
    identifier: str,
    limit_type: str,
    ip_address: str,
    device_fingerprint: str,
    latitude: float,
    longitude: float,
    radius: Optional[int] = None,
    user_id: Optional[int] = None,
    device_model: Optional[str] = None,
    app_version: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> bool:
    """
    Log a rate limit exceeded incident.
    
    Convenience function for logging rate limit violations.
    
    Args:
        identifier: IP address or device fingerprint that exceeded limit
        limit_type: "IP" or "DEVICE"
        ip_address: Client IP address
        device_fingerprint: Device fingerprint
        latitude: GPS latitude
        longitude: GPS longitude
        radius: Alert radius (optional)
        user_id: User ID (optional)
        device_model: Device model (optional)
        app_version: App version (optional)
        user_agent: User-Agent header (optional)
        
    Returns:
        True if logging successful
    """
    if limit_type == "IP":
        result = "RATE_LIMITED_IP"
        reason = f"IP rate limit exceeded: {identifier}"
    elif limit_type == "DEVICE":
        result = "RATE_LIMITED_DEVICE"
        reason = f"Device rate limit exceeded: {identifier}"
    else:
        logger.error(f"Unknown limit type: {limit_type}")
        return False
    
    return log_sos_attempt(
        sos_alert_id=None,
        ip_address=ip_address,
        device_fingerprint=device_fingerprint,
        latitude=latitude,
        longitude=longitude,
        radius=radius,
        rate_limit_ip_status="REJECT" if limit_type == "IP" else "PASS",
        rate_limit_device_status="REJECT" if limit_type == "DEVICE" else "PASS",
        geofence_status="PASS",
        result=result,
        reason=reason,
        user_id=user_id,
        device_model=device_model,
        app_version=app_version,
        user_agent=user_agent,
    )


def log_geofence_violation(
    ip_address: str,
    device_fingerprint: str,
    latitude: float,
    longitude: float,
    reason: str,
    radius: Optional[int] = None,
    user_id: Optional[int] = None,
    device_model: Optional[str] = None,
    app_version: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> bool:
    """
    Log a geofence validation violation.
    
    Convenience function for logging requests from outside operational region.
    
    Args:
        ip_address: Client IP address
        device_fingerprint: Device fingerprint
        latitude: GPS latitude
        longitude: GPS longitude
        reason: Reason for geofence violation
        radius: Alert radius (optional)
        user_id: User ID (optional)
        device_model: Device model (optional)
        app_version: App version (optional)
        user_agent: User-Agent header (optional)
        
    Returns:
        True if logging successful
    """
    return log_sos_attempt(
        sos_alert_id=None,
        ip_address=ip_address,
        device_fingerprint=device_fingerprint,
        latitude=latitude,
        longitude=longitude,
        radius=radius,
        rate_limit_ip_status="PASS",
        rate_limit_device_status="PASS",
        geofence_status="REJECT",
        result="INVALID_LOCATION",
        reason=reason,
        user_id=user_id,
        device_model=device_model,
        app_version=app_version,
        user_agent=user_agent,
    )


def log_invalid_fingerprint(
    ip_address: str,
    device_fingerprint: str,
    latitude: float,
    longitude: float,
    reason: str,
    radius: Optional[int] = None,
    user_id: Optional[int] = None,
    device_model: Optional[str] = None,
    app_version: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> bool:
    """
    Log an invalid device fingerprint incident.
    
    Convenience function for logging requests with invalid fingerprints.
    
    Args:
        ip_address: Client IP address
        device_fingerprint: Invalid device fingerprint
        latitude: GPS latitude
        longitude: GPS longitude
        reason: Reason for invalid fingerprint
        radius: Alert radius (optional)
        user_id: User ID (optional)
        device_model: Device model (optional)
        app_version: App version (optional)
        user_agent: User-Agent header (optional)
        
    Returns:
        True if logging successful
    """
    return log_sos_attempt(
        sos_alert_id=None,
        ip_address=ip_address,
        device_fingerprint=device_fingerprint,
        latitude=latitude,
        longitude=longitude,
        radius=radius,
        rate_limit_ip_status="PASS",
        rate_limit_device_status="PASS",
        geofence_status="PASS",
        result="INVALID_FINGERPRINT",
        reason=reason,
        user_id=user_id,
        device_model=device_model,
        app_version=app_version,
        user_agent=user_agent,
    )
