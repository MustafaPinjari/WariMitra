"""
Geofence Validator Module
Phase 1.2 Implementation: DDoS Protection

Validates that SOS alerts originate from within the operational region (India).
Uses simple rectangular bounds checking for O(1) performance.

India Bounds (simplified):
- North: 35.5°N (Jammu & Kashmir)
- South: 8.0°N (Kanyakumari)
- East: 97.0°E (Arunachal Pradesh)
- West: 68.0°E (Gujarat)
- Tolerance: ±0.045 degrees (~5km at equator)

Example:
    from apps.sos.geofence import GeofenceValidator
    
    validator = GeofenceValidator()
    
    # Check if location is valid
    is_valid, reason = validator.validate(latitude=28.6139, longitude=77.2090)
    
    if not is_valid:
        return Response({"error": "invalid_location", "reason": reason}, status=400)
"""
import logging
from typing import Tuple, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class GeofenceValidator:
    """
    Validates GPS coordinates are within operational region (India) with tolerance.
    
    Uses point-in-rectangle algorithm for O(1) performance:
    1. Extract latitude and longitude from request
    2. Check if within bounds (with tolerance margin)
    3. Return True if valid, False with reason if invalid
    
    Attributes:
        bounds: Dictionary with North, South, East, West boundaries
        tolerance: Margin in degrees (~5km)
    """
    
    # India geographical bounds (simplified rectangular bounds)
    DEFAULT_BOUNDS = {
        'north': 35.5,      # Jammu & Kashmir / PoK border
        'south': 8.0,       # South India
        'east': 97.0,       # Arunachal Pradesh / Myanmar border
        'west': 68.0,       # Kutch / Pakistan border
    }
    
    # Tolerance in degrees (~5km at equator, varies with latitude)
    DEFAULT_TOLERANCE_KM = 5
    # 1 degree latitude = ~111 km
    # 1 degree longitude = ~111 km * cos(latitude), but we use simplified 111 km
    DEGREES_PER_KM = 1.0 / 111.0  # ~0.009 degrees per km
    DEFAULT_TOLERANCE_DEGREES = DEFAULT_TOLERANCE_KM * DEGREES_PER_KM  # ~0.045
    
    # Result codes
    RESULT_VALID = "valid"
    RESULT_LATITUDE_TOO_NORTH = "latitude_too_north"
    RESULT_LATITUDE_TOO_SOUTH = "latitude_too_south"
    RESULT_LONGITUDE_TOO_EAST = "longitude_too_east"
    RESULT_LONGITUDE_TOO_WEST = "longitude_too_west"
    RESULT_INVALID_COORDINATES = "invalid_coordinates"
    
    def __init__(
        self,
        bounds: Optional[dict] = None,
        tolerance_km: Optional[float] = None
    ):
        """
        Initialize geofence validator.
        
        Args:
            bounds: Custom bounds dict with keys: north, south, east, west
                   (default: India bounds)
            tolerance_km: Tolerance margin in kilometers
                         (default: 5km)
        """
        # Load configuration from settings if available
        config = getattr(settings, 'GEOFENCE_CONFIG', {})
        
        # Use provided bounds or from settings or defaults
        if bounds:
            self.bounds = bounds
        elif 'BOUNDS' in config:
            self.bounds = config['BOUNDS']
        else:
            self.bounds = self.DEFAULT_BOUNDS
        
        # Use provided tolerance or from settings or default
        if tolerance_km is not None:
            self.tolerance_km = tolerance_km
        else:
            self.tolerance_km = config.get('MARGIN_KM', self.DEFAULT_TOLERANCE_KM)
        
        # Convert tolerance to degrees
        self.tolerance_degrees = self.tolerance_km * self.DEGREES_PER_KM
    
    def validate(
        self,
        latitude: Optional[float],
        longitude: Optional[float]
    ) -> Tuple[bool, str]:
        """
        Validate that coordinates are within operational region.
        
        Checks:
        1. Latitude and longitude are valid numbers
        2. Latitude within valid range (-90 to 90)
        3. Longitude within valid range (-180 to 180)
        4. Coordinates within India bounds (with tolerance)
        
        Args:
            latitude: Latitude coordinate (-90 to 90)
            longitude: Longitude coordinate (-180 to 180)
            
        Returns:
            Tuple (is_valid: bool, reason: str)
            - (True, "valid") if within bounds
            - (False, reason) if outside bounds with specific reason
            
        Example:
            >>> validator = GeofenceValidator()
            >>> is_valid, reason = validator.validate(28.6139, 77.2090)
            >>> if not is_valid:
            ...     print(f"Invalid: {reason}")
        """
        # Validate input types
        try:
            latitude = float(latitude) if latitude is not None else None
            longitude = float(longitude) if longitude is not None else None
        except (TypeError, ValueError):
            logger.warning(
                f"Invalid coordinate types: lat={type(latitude)}, "
                f"lon={type(longitude)}"
            )
            return False, self.RESULT_INVALID_COORDINATES
        
        # Check for None values
        if latitude is None or longitude is None:
            logger.warning(f"Missing coordinates: lat={latitude}, lon={longitude}")
            return False, self.RESULT_INVALID_COORDINATES
        
        # Check valid ranges
        if not (-90 <= latitude <= 90):
            logger.warning(f"Latitude out of global range: {latitude}")
            return False, self.RESULT_INVALID_COORDINATES
        
        if not (-180 <= longitude <= 180):
            logger.warning(f"Longitude out of global range: {longitude}")
            return False, self.RESULT_INVALID_COORDINATES
        
        # Check against bounds with tolerance
        b = self.bounds
        m = self.tolerance_degrees
        
        # Latitude checks
        if latitude > b['north'] + m:
            logger.warning(
                f"Latitude too far north: {latitude} > {b['north'] + m}"
            )
            return False, self.RESULT_LATITUDE_TOO_NORTH
        
        if latitude < b['south'] - m:
            logger.warning(
                f"Latitude too far south: {latitude} < {b['south'] - m}"
            )
            return False, self.RESULT_LATITUDE_TOO_SOUTH
        
        # Longitude checks
        if longitude > b['east'] + m:
            logger.warning(
                f"Longitude too far east: {longitude} > {b['east'] + m}"
            )
            return False, self.RESULT_LONGITUDE_TOO_EAST
        
        if longitude < b['west'] - m:
            logger.warning(
                f"Longitude too far west: {longitude} < {b['west'] - m}"
            )
            return False, self.RESULT_LONGITUDE_TOO_WEST
        
        # All checks passed
        return True, self.RESULT_VALID
    
    def get_human_readable_reason(self, reason_code: str) -> str:
        """
        Convert reason code to human-readable message.
        
        Args:
            reason_code: Result code from validate()
            
        Returns:
            Human-readable reason string
            
        Example:
            >>> validator = GeofenceValidator()
            >>> is_valid, reason = validator.validate(52.52, 13.40)  # Berlin
            >>> readable = validator.get_human_readable_reason(reason)
            >>> print(readable)  # "Location is too far north of operational region"
        """
        reason_messages = {
            self.RESULT_VALID: "Location is valid (within operational region)",
            self.RESULT_LATITUDE_TOO_NORTH: (
                f"Location is too far north (> {self.bounds['north'] + self.tolerance_degrees}°N)"
            ),
            self.RESULT_LATITUDE_TOO_SOUTH: (
                f"Location is too far south (< {self.bounds['south'] - self.tolerance_degrees}°N)"
            ),
            self.RESULT_LONGITUDE_TOO_EAST: (
                f"Location is too far east (> {self.bounds['east'] + self.tolerance_degrees}°E)"
            ),
            self.RESULT_LONGITUDE_TOO_WEST: (
                f"Location is too far west (< {self.bounds['west'] - self.tolerance_degrees}°E)"
            ),
            self.RESULT_INVALID_COORDINATES: "Invalid coordinates provided",
        }
        
        return reason_messages.get(reason_code, "Unknown reason")
    
    def get_bounds_with_tolerance(self) -> dict:
        """
        Get effective bounds including tolerance margin.
        
        Returns:
            Dictionary with effective bounds after applying tolerance
            
        Example:
            >>> validator = GeofenceValidator()
            >>> bounds = validator.get_bounds_with_tolerance()
            >>> print(f"Effective bounds: {bounds}")
        """
        m = self.tolerance_degrees
        
        return {
            'north': self.bounds['north'] + m,
            'south': self.bounds['south'] - m,
            'east': self.bounds['east'] + m,
            'west': self.bounds['west'] - m,
        }
    
    def distance_from_boundary(
        self,
        latitude: float,
        longitude: float
    ) -> Optional[dict]:
        """
        Calculate approximate distance from boundaries (for monitoring/debugging).
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Dictionary with distances to boundaries, or None if error
            
        Example:
            >>> validator = GeofenceValidator()
            >>> distances = validator.distance_from_boundary(52.52, 13.40)
            >>> print(f"Too far north by: {distances['to_north_boundary']} km")
        """
        try:
            b = self.bounds
            
            # Distance calculations (simplified, not accounting for latitude)
            distances = {
                'to_north_boundary': (b['north'] - latitude) * 111,  # km
                'to_south_boundary': (latitude - b['south']) * 111,  # km
                'to_east_boundary': (b['east'] - longitude) * 111 * 0.7,  # Approximate
                'to_west_boundary': (longitude - b['west']) * 111 * 0.7,  # Approximate
                'min_distance': None,  # Will be filled below
            }
            
            # Find minimum distance
            min_dist = min(
                abs(distances['to_north_boundary']),
                abs(distances['to_south_boundary']),
                abs(distances['to_east_boundary']),
                abs(distances['to_west_boundary'])
            )
            distances['min_distance'] = min_dist
            
            return distances
        
        except Exception as e:
            logger.error(f"Error calculating distance from boundary: {str(e)}")
            return None
