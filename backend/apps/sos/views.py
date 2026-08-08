"""
SOS Views with DDoS Protection
Phase 1.2 Implementation: Three-layer DDoS protection

Implements:
1. Device fingerprint validation
2. IP-based rate limiting (100 req/min)
3. Device-based rate limiting (5 req/min)
4. Geofence validation (India bounds)
5. Audit logging for all attempts
"""
import logging
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from .models import SosAlert
from .serializers import SosAlertSerializer
from .rate_limiter import RateLimiter
from .device_fingerprint import DeviceFingerprintValidator
from .geofence import GeofenceValidator
from .logging import (
    log_sos_attempt,
    log_rate_limit_exceeded,
    log_geofence_violation,
    log_invalid_fingerprint,
)

logger = logging.getLogger(__name__)

# Initialize protection modules
rate_limiter = RateLimiter()
fingerprint_validator = DeviceFingerprintValidator()
geofence_validator = GeofenceValidator()


def get_client_ip(request):
    """
    Extract client IP from request, handling proxies.
    
    Checks X-Forwarded-For header first (for proxies/load balancers),
    then falls back to REMOTE_ADDR.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # X-Forwarded-For can have multiple IPs, take the first
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
    return ip


class SosAlertViewSet(viewsets.ModelViewSet):
    """
    SOS Alert viewset with comprehensive DDoS protection.
    
    Implements three-layer defense:
    1. Device Fingerprint Validation - Verify fingerprint format
    2. IP Rate Limiting - 100 requests/minute per IP
    3. Device Rate Limiting - 5 requests/minute per device
    4. Geofence Validation - Only allow requests from India
    5. Audit Logging - Log all attempts
    
    All checks are performed in order and fail-fast on first violation.
    """
    queryset = SosAlert.objects.filter(is_active=True)
    serializer_class = SosAlertSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        """
        Create SOS alert with DDoS protection checks.
        
        Request body:
        {
            "latitude": 28.6139,
            "longitude": 77.2090,
            "radius": 1000,
            "device_fingerprint": "abc123def456...",
            "device_model": "iPhone12" (optional),
            "app_version": "1.2.3" (optional)
        }
        
        Response:
        - 201: Alert created successfully
        - 400: Invalid request (fingerprint, geofence, etc.)
        - 429: Rate limited (IP or device)
        
        All attempts logged to SOSAuditLog for audit trail.
        """
        # Extract required and optional data
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        radius = request.data.get('radius', 1000)
        device_fingerprint = request.data.get('device_fingerprint', '').strip()
        device_model = request.data.get('device_model', '')
        app_version = request.data.get('app_version', '')
        
        # Get client information
        client_ip = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        user_id = request.user.id if request.user.is_authenticated else None
        
        logger.info(
            f"SOS creation attempt from IP: {client_ip}, "
            f"FP: {device_fingerprint[:12] if device_fingerprint else 'NONE'}..., "
            f"Loc: ({latitude}, {longitude})"
        )
        
        # ========== CHECK 1: Device Fingerprint Validation ==========
        if not device_fingerprint:
            logger.warning(f"Missing device fingerprint from IP: {client_ip}")
            
            # Log attempt with invalid fingerprint
            log_invalid_fingerprint(
                ip_address=client_ip,
                device_fingerprint='',
                latitude=latitude or 0.0,
                longitude=longitude or 0.0,
                reason="Device fingerprint required but not provided",
                radius=radius,
                user_id=user_id,
                device_model=device_model,
                app_version=app_version,
                user_agent=user_agent,
            )
            
            return Response(
                {
                    "error": "missing_device_fingerprint",
                    "message": "device_fingerprint is required",
                    "detail": "Device fingerprint must be provided in request body"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate fingerprint format
        if not fingerprint_validator.validate_fingerprint(device_fingerprint):
            logger.warning(
                f"Invalid device fingerprint from IP: {client_ip}: "
                f"{device_fingerprint}"
            )
            
            # Log attempt with invalid fingerprint
            log_invalid_fingerprint(
                ip_address=client_ip,
                device_fingerprint=device_fingerprint,
                latitude=latitude or 0.0,
                longitude=longitude or 0.0,
                reason="Device fingerprint format invalid",
                radius=radius,
                user_id=user_id,
                device_model=device_model,
                app_version=app_version,
                user_agent=user_agent,
            )
            
            return Response(
                {
                    "error": "invalid_device_fingerprint",
                    "message": "Invalid device fingerprint format",
                    "detail": "Fingerprint must be 32-64 character hex string or UUID"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Track fingerprint for audit trail
        fingerprint_validator.track_fingerprint(
            fingerprint=device_fingerprint,
            ip_address=client_ip,
            user_agent=user_agent,
            device_model=device_model,
            app_version=app_version,
        )
        
        # ========== CHECK 2: IP Rate Limiting ==========
        if not rate_limiter.check_ip_limit(client_ip):
            logger.warning(
                f"IP rate limit exceeded: {client_ip}, "
                f"FP: {device_fingerprint[:12]}..."
            )
            
            # Log rate limit violation
            log_rate_limit_exceeded(
                identifier=client_ip,
                limit_type="IP",
                ip_address=client_ip,
                device_fingerprint=device_fingerprint,
                latitude=latitude or 0.0,
                longitude=longitude or 0.0,
                radius=radius,
                user_id=user_id,
                device_model=device_model,
                app_version=app_version,
                user_agent=user_agent,
            )
            
            return Response(
                {
                    "error": "rate_limited",
                    "message": "Too many SOS requests from this IP",
                    "detail": "Please wait before sending another SOS alert",
                    "retry_after": 60
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
                headers={'Retry-After': '60'}
            )
        
        # ========== CHECK 3: Device Rate Limiting ==========
        if not rate_limiter.check_device_limit(device_fingerprint):
            logger.warning(
                f"Device rate limit exceeded: {device_fingerprint[:12]}..., "
                f"IP: {client_ip}"
            )
            
            # Log rate limit violation
            log_rate_limit_exceeded(
                identifier=device_fingerprint,
                limit_type="DEVICE",
                ip_address=client_ip,
                device_fingerprint=device_fingerprint,
                latitude=latitude or 0.0,
                longitude=longitude or 0.0,
                radius=radius,
                user_id=user_id,
                device_model=device_model,
                app_version=app_version,
                user_agent=user_agent,
            )
            
            return Response(
                {
                    "error": "device_rate_limited",
                    "message": "This device has sent too many SOS alerts",
                    "detail": "Your device has reached the SOS request limit",
                    "retry_after": 60
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
                headers={'Retry-After': '60'}
            )
        
        # ========== CHECK 4: Geofence Validation ==========
        try:
            latitude_float = float(latitude)
            longitude_float = float(longitude)
        except (TypeError, ValueError):
            logger.warning(
                f"Invalid coordinates from IP {client_ip}: "
                f"lat={latitude}, lon={longitude}"
            )
            
            return Response(
                {
                    "error": "invalid_coordinates",
                    "message": "Invalid latitude/longitude provided",
                    "detail": "Coordinates must be valid numbers"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        is_valid, geofence_reason = geofence_validator.validate(
            latitude_float,
            longitude_float
        )
        
        if not is_valid:
            logger.warning(
                f"Geofence violation from IP {client_ip}: "
                f"lat={latitude}, lon={longitude}, "
                f"reason={geofence_reason}"
            )
            
            # Log geofence violation
            log_geofence_violation(
                ip_address=client_ip,
                device_fingerprint=device_fingerprint,
                latitude=latitude_float,
                longitude=longitude_float,
                reason=geofence_validator.get_human_readable_reason(geofence_reason),
                radius=radius,
                user_id=user_id,
                device_model=device_model,
                app_version=app_version,
                user_agent=user_agent,
            )
            
            return Response(
                {
                    "error": "invalid_location",
                    "message": "SOS alert outside operational region",
                    "detail": geofence_validator.get_human_readable_reason(geofence_reason),
                    "reason": geofence_reason
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # ========== ALL CHECKS PASSED: Create Alert ==========
        try:
            # Create SOS alert
            sos_alert = SosAlert.objects.create(
                user=request.user,
                latitude=latitude_float,
                longitude=longitude_float,
                radius=radius,
                status='pending',
                severity='high'  # SOS alerts are high severity by default
            )
            
            logger.info(
                f"SOS alert created: ID={sos_alert.id}, "
                f"User={request.user.username}, "
                f"Loc=({latitude_float}, {longitude_float})"
            )
            
            # Log successful attempt
            log_sos_attempt(
                sos_alert_id=sos_alert.id,
                ip_address=client_ip,
                device_fingerprint=device_fingerprint,
                latitude=latitude_float,
                longitude=longitude_float,
                radius=radius,
                rate_limit_ip_status="PASS",
                rate_limit_device_status="PASS",
                geofence_status="PASS",
                result="SUCCESS",
                user_id=user_id,
                device_model=device_model,
                app_version=app_version,
                user_agent=user_agent,
            )
            
            # Serialize and return
            serializer = self.get_serializer(sos_alert)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(
                f"Error creating SOS alert: {str(e)}",
                exc_info=True,
                extra={'user': request.user.id, 'ip': client_ip}
            )
            
            # Log error
            log_sos_attempt(
                sos_alert_id=None,
                ip_address=client_ip,
                device_fingerprint=device_fingerprint,
                latitude=latitude_float,
                longitude=longitude_float,
                radius=radius,
                rate_limit_ip_status="PASS",
                rate_limit_device_status="PASS",
                geofence_status="PASS",
                result="ERROR",
                reason=str(e),
                user_id=user_id,
                device_model=device_model,
                app_version=app_version,
                user_agent=user_agent,
            )
            
            return Response(
                {
                    "error": "internal_error",
                    "message": "Failed to create SOS alert",
                    "detail": "An error occurred while processing your request"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def perform_create(self, serializer):
        """Original perform_create (may not be called with custom create)"""
        serializer.save(user=self.request.user)
