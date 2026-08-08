"""
Device Fingerprint Validator Module
Phase 1.2 Implementation: DDoS Protection

Validates and tracks device fingerprints to prevent spoofing and enable per-device rate limiting.
Device fingerprints are generated on mobile clients and stored persistently across app restarts.

Example:
    from apps.sos.device_fingerprint import DeviceFingerprintValidator
    
    validator = DeviceFingerprintValidator()
    
    # Validate format
    if not validator.validate_fingerprint("abc123def456"):
        return Response({"error": "Invalid fingerprint"}, status=400)
    
    # Track fingerprint (device first seen)
    validator.track_fingerprint(
        fingerprint="abc123def456",
        ip_address="192.168.1.1",
        user_agent="Mozilla/5.0..."
    )
"""
import logging
import re
from typing import Tuple, Optional
from django.db import IntegrityError
from apps.sos.models import DeviceFingerprint

logger = logging.getLogger(__name__)


class DeviceFingerprintValidator:
    """
    Validates and tracks device fingerprints for SOS protection.
    
    Fingerprint Format:
    - 64-character hexadecimal string (SHA256 hash)
    - Generated from: ANDROID_ID (Android) or IDFV (iOS) + device model + OS version
    - Example: "abc123def456..." (64 chars)
    
    Fingerprints are stored on device and persist across:
    - App restarts
    - OS updates
    - Minor app updates
    
    Should be cleared on:
    - Factory reset
    - Device theft/loss (manual action)
    
    Attributes:
        max_length: Maximum fingerprint length (default: 64 for SHA256)
        hex_pattern: Regex pattern for valid fingerprint format
    """
    
    # Fingerprint constraints
    MAX_LENGTH = 64
    # Regex pattern: 64 lowercase hex characters (SHA256) or 32 hex chars (MD5) or 36 char UUID
    HEX_PATTERN = re.compile(r'^[a-f0-9]{32,64}$', re.IGNORECASE)
    UUID_PATTERN = re.compile(
        r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$',
        re.IGNORECASE
    )
    
    def __init__(self):
        """Initialize device fingerprint validator"""
        pass
    
    def validate_fingerprint(self, fingerprint: Optional[str]) -> bool:
        """
        Validate device fingerprint format and length.
        
        Checks:
        1. Not empty or None
        2. Length <= 64 characters
        3. Valid format: hexadecimal string or UUID
        4. No special characters that could cause injection
        
        Args:
            fingerprint: Device fingerprint to validate
            
        Returns:
            True if valid format, False otherwise
            
        Example:
            >>> validator = DeviceFingerprintValidator()
            >>> validator.validate_fingerprint("abc123def456")
            True
            >>> validator.validate_fingerprint("invalid!")
            False
            >>> validator.validate_fingerprint("")
            False
        """
        # Check if empty or None
        if not fingerprint or not isinstance(fingerprint, str):
            logger.warning(f"Invalid fingerprint type: {type(fingerprint)}")
            return False
        
        # Check length
        if len(fingerprint) > self.MAX_LENGTH:
            logger.warning(
                f"Fingerprint too long: {len(fingerprint)} > {self.MAX_LENGTH}"
            )
            return False
        
        # Check minimum length (at least MD5 32 chars)
        if len(fingerprint) < 32:
            logger.warning(
                f"Fingerprint too short: {len(fingerprint)} < 32"
            )
            return False
        
        # Check format: hex string or UUID
        if not (self.HEX_PATTERN.match(fingerprint) or 
                self.UUID_PATTERN.match(fingerprint)):
            logger.warning(f"Fingerprint invalid format: {fingerprint}")
            return False
        
        return True
    
    def track_fingerprint(
        self,
        fingerprint: str,
        ip_address: str,
        user_agent: Optional[str] = None,
        device_model: Optional[str] = None,
        app_version: Optional[str] = None,
        os_version: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Track a device fingerprint in database for audit trail.
        
        Records first time a device fingerprint is seen. Subsequent calls
        with same fingerprint are ignored (duplicate keys prevented by DB).
        
        Args:
            fingerprint: Device fingerprint (64-char hex string)
            ip_address: IP address where fingerprint was first seen
            user_agent: User-Agent header (optional)
            device_model: Device model string (optional, e.g., "iPhone12")
            app_version: App version string (optional, e.g., "1.2.3")
            os_version: OS version string (optional, e.g., "14.5")
            
        Returns:
            Tuple (success: bool, error_message: Optional[str])
            - (True, None) if fingerprint tracked successfully
            - (False, error_message) if error occurs
            
        Example:
            >>> validator = DeviceFingerprintValidator()
            >>> success, error = validator.track_fingerprint(
            ...     fingerprint="abc123def456...",
            ...     ip_address="192.168.1.1",
            ...     user_agent="MobileApp/1.0",
            ...     device_model="iPhone12",
            ...     app_version="1.2.3",
            ...     os_version="14.5"
            ... )
            >>> if success:
            ...     print("Fingerprint tracked")
            >>> else:
            ...     print(f"Error: {error}")
        """
        try:
            # Validate fingerprint format first
            if not self.validate_fingerprint(fingerprint):
                error = f"Invalid fingerprint format: {fingerprint}"
                logger.warning(error)
                return False, error
            
            # Create or get fingerprint record
            # Unique constraint prevents duplicates
            fp_obj, created = DeviceFingerprint.objects.get_or_create(
                fingerprint=fingerprint,
                defaults={
                    'ip_address': ip_address,
                    'user_agent': user_agent or '',
                    'device_model': device_model or '',
                    'app_version': app_version or '',
                    'os_version': os_version or '',
                }
            )
            
            if created:
                logger.info(
                    f"New fingerprint tracked: {fingerprint[:16]}... "
                    f"from IP: {ip_address}, device: {device_model}"
                )
            else:
                logger.debug(
                    f"Fingerprint already tracked: {fingerprint[:16]}... "
                    f"(first seen at: {fp_obj.created_at})"
                )
            
            return True, None
            
        except IntegrityError as e:
            # Unique constraint violation (shouldn't happen with get_or_create)
            error = f"Fingerprint integrity error: {str(e)}"
            logger.warning(error)
            return False, error
        
        except Exception as e:
            error = f"Error tracking fingerprint: {str(e)}"
            logger.error(error, exc_info=True)
            return False, error
    
    def get_fingerprint_info(self, fingerprint: str) -> Optional[dict]:
        """
        Get information about a tracked fingerprint.
        
        Args:
            fingerprint: Device fingerprint to look up
            
        Returns:
            Dictionary with fingerprint info, or None if not found
            
        Example:
            >>> validator = DeviceFingerprintValidator()
            >>> info = validator.get_fingerprint_info("abc123def456...")
            >>> if info:
            ...     print(f"First seen: {info['created_at']}")
            ...     print(f"IP: {info['ip_address']}")
        """
        try:
            fp_obj = DeviceFingerprint.objects.get(fingerprint=fingerprint)
            
            return {
                'fingerprint': fp_obj.fingerprint,
                'created_at': fp_obj.created_at,
                'ip_address': fp_obj.ip_address,
                'user_agent': fp_obj.user_agent,
                'device_model': fp_obj.device_model,
                'app_version': fp_obj.app_version,
                'os_version': fp_obj.os_version,
            }
        
        except DeviceFingerprint.DoesNotExist:
            logger.debug(f"Fingerprint not found in database: {fingerprint[:16]}...")
            return None
        
        except Exception as e:
            logger.error(f"Error retrieving fingerprint info: {str(e)}", exc_info=True)
            return None
    
    def is_fingerprint_known(self, fingerprint: str) -> bool:
        """
        Check if a fingerprint has been seen before.
        
        Args:
            fingerprint: Device fingerprint to check
            
        Returns:
            True if fingerprint is in database, False otherwise
            
        Example:
            >>> validator = DeviceFingerprintValidator()
            >>> if validator.is_fingerprint_known("abc123def456..."):
            ...     print("Known device")
        """
        try:
            return DeviceFingerprint.objects.filter(
                fingerprint=fingerprint
            ).exists()
        
        except Exception as e:
            logger.error(f"Error checking fingerprint existence: {str(e)}")
            return False
    
    def count_fingerprints(self) -> int:
        """
        Get total count of tracked fingerprints (for monitoring).
        
        Returns:
            Number of unique fingerprints in database
        """
        try:
            return DeviceFingerprint.objects.count()
        except Exception as e:
            logger.error(f"Error counting fingerprints: {str(e)}")
            return 0
    
    @staticmethod
    def validate_fingerprint_format(fingerprint: Optional[str]) -> bool:
        """
        Static method for simple fingerprint format validation.
        
        Args:
            fingerprint: Fingerprint to validate
            
        Returns:
            True if valid format
            
        Example:
            >>> if DeviceFingerprintValidator.validate_fingerprint_format(fp):
            ...     # Process request
        """
        validator = DeviceFingerprintValidator()
        return validator.validate_fingerprint(fingerprint)
