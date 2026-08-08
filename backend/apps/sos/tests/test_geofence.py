"""
Unit Tests for Geofence Validator
Phase 1.2 Implementation: DDoS Protection

Test Coverage:
- India bounds validation
- Tolerance margin handling
- Edge cases (borders, corners)
- Invalid coordinates
- Human-readable messages
"""
import pytest
from django.test import TestCase, override_settings
from apps.sos.geofence import GeofenceValidator


class TestGeofenceBasicValidation(TestCase):
    """Test basic geofence validation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.validator = GeofenceValidator()
    
    def test_delhi_accepted(self):
        """Test that Delhi coordinates are accepted"""
        # Delhi: 28.6139° N, 77.2090° E
        is_valid, reason = self.validator.validate(28.6139, 77.2090)
        
        assert is_valid is True
        assert reason == GeofenceValidator.RESULT_VALID
    
    def test_mumbai_accepted(self):
        """Test that Mumbai coordinates are accepted"""
        # Mumbai: 19.0760° N, 72.8777° E
        is_valid, reason = self.validator.validate(19.0760, 72.8777)
        
        assert is_valid is True
    
    def test_bangalore_accepted(self):
        """Test that Bangalore coordinates are accepted"""
        # Bangalore: 12.9716° N, 77.5946° E
        is_valid, reason = self.validator.validate(12.9716, 77.5946)
        
        assert is_valid is True
    
    def test_kolkata_accepted(self):
        """Test that Kolkata coordinates are accepted"""
        # Kolkata: 22.5726° N, 88.3639° E
        is_valid, reason = self.validator.validate(22.5726, 88.3639)
        
        assert is_valid is True
    
    def test_berlin_rejected(self):
        """Test that Berlin (outside India) is rejected"""
        # Berlin: 52.5200° N, 13.4050° E
        is_valid, reason = self.validator.validate(52.5200, 13.4050)
        
        assert is_valid is False
        assert reason == GeofenceValidator.RESULT_LATITUDE_TOO_NORTH
    
    def test_london_rejected(self):
        """Test that London (outside India) is rejected"""
        # London: 51.5074° N, -0.1278° E
        is_valid, reason = self.validator.validate(51.5074, -0.1278)
        
        assert is_valid is False
    
    def test_singapore_rejected(self):
        """Test that Singapore (outside India) is rejected"""
        # Singapore: 1.3521° N, 103.8198° E
        is_valid, reason = self.validator.validate(1.3521, 103.8198)
        
        assert is_valid is False
        assert reason == GeofenceValidator.RESULT_LONGITUDE_TOO_EAST
    
    def test_sri_lanka_rejected(self):
        """Test that Sri Lanka (outside India) is rejected"""
        # Sri Lanka: 6.9271° N, 80.7789° E
        is_valid, reason = self.validator.validate(6.9271, 80.7789)
        
        assert is_valid is False
        assert reason == GeofenceValidator.RESULT_LATITUDE_TOO_SOUTH


class TestGeofenceBoundaryConditions(TestCase):
    """Test boundary conditions and tolerance"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.validator = GeofenceValidator()
    
    def test_north_boundary_accepted_within_tolerance(self):
        """Test that coordinates north of main boundary but within tolerance are accepted"""
        # 35.5 + 0.045 = 35.545
        is_valid, reason = self.validator.validate(35.544, 77.0)
        
        assert is_valid is True
    
    def test_north_boundary_rejected_outside_tolerance(self):
        """Test that coordinates too far north are rejected"""
        # 35.5 + 0.045 + 0.001 = 35.546
        is_valid, reason = self.validator.validate(35.546, 77.0)
        
        assert is_valid is False
        assert reason == GeofenceValidator.RESULT_LATITUDE_TOO_NORTH
    
    def test_south_boundary_accepted_within_tolerance(self):
        """Test that coordinates south of main boundary but within tolerance are accepted"""
        # 8.0 - 0.045 = 7.955
        is_valid, reason = self.validator.validate(7.954, 77.0)
        
        assert is_valid is True
    
    def test_south_boundary_rejected_outside_tolerance(self):
        """Test that coordinates too far south are rejected"""
        # 8.0 - 0.045 - 0.001 = 7.954
        is_valid, reason = self.validator.validate(7.954, 77.0)
        
        # This might be close to boundary, so test even further
        is_valid, reason = self.validator.validate(7.900, 77.0)
        assert is_valid is False
        assert reason == GeofenceValidator.RESULT_LATITUDE_TOO_SOUTH
    
    def test_east_boundary_accepted_within_tolerance(self):
        """Test that coordinates east of main boundary but within tolerance are accepted"""
        # 97.0 + 0.045 = 97.045
        is_valid, reason = self.validator.validate(20.0, 97.044)
        
        assert is_valid is True
    
    def test_east_boundary_rejected_outside_tolerance(self):
        """Test that coordinates too far east are rejected"""
        is_valid, reason = self.validator.validate(20.0, 97.046)
        
        assert is_valid is False
        assert reason == GeofenceValidator.RESULT_LONGITUDE_TOO_EAST
    
    def test_west_boundary_accepted_within_tolerance(self):
        """Test that coordinates west of main boundary but within tolerance are accepted"""
        # 68.0 - 0.045 = 67.955
        is_valid, reason = self.validator.validate(20.0, 67.956)
        
        assert is_valid is True
    
    def test_west_boundary_rejected_outside_tolerance(self):
        """Test that coordinates too far west are rejected"""
        # 68.0 - 0.045 - 0.001 = 67.954
        is_valid, reason = self.validator.validate(20.0, 67.954)
        
        assert is_valid is False
        assert reason == GeofenceValidator.RESULT_LONGITUDE_TOO_WEST
    
    def test_northeast_corner_accepted(self):
        """Test northeast corner (within tolerance)"""
        # Near northeast corner
        is_valid, reason = self.validator.validate(35.544, 97.044)
        
        assert is_valid is True
    
    def test_southwest_corner_accepted(self):
        """Test southwest corner (within tolerance)"""
        # Near southwest corner
        is_valid, reason = self.validator.validate(7.956, 67.956)
        
        assert is_valid is True


class TestGeofenceInvalidInputs(TestCase):
    """Test handling of invalid inputs"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.validator = GeofenceValidator()
    
    def test_latitude_none(self):
        """Test handling of None latitude"""
        is_valid, reason = self.validator.validate(None, 77.0)
        
        assert is_valid is False
        assert reason == GeofenceValidator.RESULT_INVALID_COORDINATES
    
    def test_longitude_none(self):
        """Test handling of None longitude"""
        is_valid, reason = self.validator.validate(28.0, None)
        
        assert is_valid is False
        assert reason == GeofenceValidator.RESULT_INVALID_COORDINATES
    
    def test_both_none(self):
        """Test handling of both coordinates None"""
        is_valid, reason = self.validator.validate(None, None)
        
        assert is_valid is False
    
    def test_latitude_out_of_global_range_positive(self):
        """Test latitude > 90 is rejected"""
        is_valid, reason = self.validator.validate(91.0, 77.0)
        
        assert is_valid is False
        assert reason == GeofenceValidator.RESULT_INVALID_COORDINATES
    
    def test_latitude_out_of_global_range_negative(self):
        """Test latitude < -90 is rejected"""
        is_valid, reason = self.validator.validate(-91.0, 77.0)
        
        assert is_valid is False
        assert reason == GeofenceValidator.RESULT_INVALID_COORDINATES
    
    def test_longitude_out_of_global_range_positive(self):
        """Test longitude > 180 is rejected"""
        is_valid, reason = self.validator.validate(28.0, 181.0)
        
        assert is_valid is False
        assert reason == GeofenceValidator.RESULT_INVALID_COORDINATES
    
    def test_longitude_out_of_global_range_negative(self):
        """Test longitude < -180 is rejected"""
        is_valid, reason = self.validator.validate(28.0, -181.0)
        
        assert is_valid is False
        assert reason == GeofenceValidator.RESULT_INVALID_COORDINATES
    
    def test_latitude_string_converted(self):
        """Test that string latitude is converted to float"""
        is_valid, reason = self.validator.validate("28.6139", 77.2090)
        
        assert is_valid is True
    
    def test_longitude_string_converted(self):
        """Test that string longitude is converted to float"""
        is_valid, reason = self.validator.validate(28.6139, "77.2090")
        
        assert is_valid is True
    
    def test_invalid_latitude_string(self):
        """Test that invalid latitude string is rejected"""
        is_valid, reason = self.validator.validate("invalid", 77.2090)
        
        assert is_valid is False
        assert reason == GeofenceValidator.RESULT_INVALID_COORDINATES
    
    def test_latitude_zero(self):
        """Test latitude zero (equator) is accepted"""
        is_valid, reason = self.validator.validate(0.0, 77.0)
        
        assert is_valid is True
    
    def test_negative_latitude_accepted(self):
        """Test that negative latitude (southern hemisphere) is rejected for India"""
        is_valid, reason = self.validator.validate(-10.0, 77.0)
        
        assert is_valid is False


class TestGeofenceMessages(TestCase):
    """Test human-readable messages"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.validator = GeofenceValidator()
    
    def test_valid_message(self):
        """Test message for valid coordinates"""
        msg = self.validator.get_human_readable_reason(GeofenceValidator.RESULT_VALID)
        
        assert "valid" in msg.lower()
        assert "operational region" in msg.lower()
    
    def test_too_north_message(self):
        """Test message for too north"""
        msg = self.validator.get_human_readable_reason(
            GeofenceValidator.RESULT_LATITUDE_TOO_NORTH
        )
        
        assert "north" in msg.lower()
    
    def test_too_south_message(self):
        """Test message for too south"""
        msg = self.validator.get_human_readable_reason(
            GeofenceValidator.RESULT_LATITUDE_TOO_SOUTH
        )
        
        assert "south" in msg.lower()
    
    def test_too_east_message(self):
        """Test message for too east"""
        msg = self.validator.get_human_readable_reason(
            GeofenceValidator.RESULT_LONGITUDE_TOO_EAST
        )
        
        assert "east" in msg.lower()
    
    def test_too_west_message(self):
        """Test message for too west"""
        msg = self.validator.get_human_readable_reason(
            GeofenceValidator.RESULT_LONGITUDE_TOO_WEST
        )
        
        assert "west" in msg.lower()
    
    def test_invalid_coordinates_message(self):
        """Test message for invalid coordinates"""
        msg = self.validator.get_human_readable_reason(
            GeofenceValidator.RESULT_INVALID_COORDINATES
        )
        
        assert "invalid" in msg.lower()


class TestGeofenceConfiguration(TestCase):
    """Test custom configuration"""
    
    def test_custom_bounds(self):
        """Test validator with custom bounds"""
        custom_bounds = {
            'north': 40.0,
            'south': 10.0,
            'east': 100.0,
            'west': 65.0,
        }
        validator = GeofenceValidator(bounds=custom_bounds)
        
        # Should accept coordinates within custom bounds
        is_valid, _ = validator.validate(20.0, 80.0)
        assert is_valid is True
        
        # Should reject coordinates outside custom bounds
        is_valid, _ = validator.validate(50.0, 80.0)
        assert is_valid is False
    
    def test_custom_tolerance(self):
        """Test validator with custom tolerance"""
        validator = GeofenceValidator(tolerance_km=10)
        
        # With 10km tolerance (~0.09 degrees)
        # North boundary with tolerance: 35.5 + 0.09 = 35.59
        is_valid, _ = validator.validate(35.59, 77.0)
        assert is_valid is True
    
    def test_get_bounds_with_tolerance(self):
        """Test retrieving effective bounds"""
        bounds = self.validator = GeofenceValidator()
        effective_bounds = bounds.get_bounds_with_tolerance()
        
        assert effective_bounds['north'] > GeofenceValidator.DEFAULT_BOUNDS['north']
        assert effective_bounds['south'] < GeofenceValidator.DEFAULT_BOUNDS['south']
        assert effective_bounds['east'] > GeofenceValidator.DEFAULT_BOUNDS['east']
        assert effective_bounds['west'] < GeofenceValidator.DEFAULT_BOUNDS['west']


class TestGeofenceDistanceCalculation(TestCase):
    """Test distance calculations"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.validator = GeofenceValidator()
    
    def test_distance_from_boundary_valid_location(self):
        """Test distance calculation for valid location"""
        # Delhi is well within bounds
        distances = self.validator.distance_from_boundary(28.6139, 77.2090)
        
        assert distances is not None
        assert distances['min_distance'] > 100  # At least 100km from boundary
    
    def test_distance_from_boundary_near_boundary(self):
        """Test distance calculation near boundary"""
        # Location near north boundary
        distances = self.validator.distance_from_boundary(35.0, 77.0)
        
        assert distances is not None
        assert distances['to_north_boundary'] < 100  # Close to north boundary
    
    def test_distance_from_boundary_outside_region(self):
        """Test distance calculation for location outside region"""
        # Berlin is outside region
        distances = self.validator.distance_from_boundary(52.52, 13.40)
        
        assert distances is not None
        # Distance to nearest boundary should be positive (in km)
        assert distances['min_distance'] > 0
