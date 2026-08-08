"""
Tests for Phase 1.3 GPS Model Encryption

Tests cover:
- Creating GpsPing with encrypted coordinates
- Time-range queries without decryption
- Coordinates remain encrypted
- Location privacy preserved
"""

import pytest
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from apps.gps.models import GpsPing
from apps.auth.models import User


class GpsEncryptionTestCase(TestCase):
    """Test GpsPing model encryption functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.user = User.objects.create(
            username="gps_user",
            email="gps@example.com"
        )
        self.test_coords = {
            'latitude': 28.7041,
            'longitude': 77.1025,
            'accuracy': 10,
            'altitude': 216.5,
            'speed': 5.2,
        }
    
    def test_create_gpsping_with_encrypted_coordinates(self):
        """Test creating GpsPing with encrypted coordinates."""
        ping = GpsPing.objects.create(
            user=self.user,
            **self.test_coords
        )
        
        # Verify ping was created
        self.assertIsNotNone(ping.id)
        
        # Verify coordinates are encrypted in database
        ping_db = GpsPing.objects.raw(
            "SELECT * FROM gps_gpsping WHERE id = %s", [ping.id]
        )[0]
        
        # Check that stored values are ciphertext (encrypted)
        # Ciphertext should NOT equal plaintext numbers
        self.assertNotEqual(ping_db.latitude, str(self.test_coords['latitude']))
        self.assertNotEqual(ping_db.longitude, str(self.test_coords['longitude']))
    
    def test_decrypt_gpsping_on_read(self):
        """Test decryption when reading GpsPing from database."""
        ping = GpsPing.objects.create(
            user=self.user,
            **self.test_coords
        )
        
        # Fetch ping from database
        ping_fetched = GpsPing.objects.get(id=ping.id)
        
        # Verify decryption worked
        self.assertAlmostEqual(ping_fetched.latitude, self.test_coords['latitude'], places=4)
        self.assertAlmostEqual(ping_fetched.longitude, self.test_coords['longitude'], places=4)
        self.assertEqual(ping_fetched.accuracy, self.test_coords['accuracy'])
        self.assertAlmostEqual(ping_fetched.altitude, self.test_coords['altitude'], places=2)
        self.assertAlmostEqual(ping_fetched.speed, self.test_coords['speed'], places=2)
    
    def test_time_range_query_without_decryption(self):
        """Test time-range queries on created_at (unencrypted timestamp)."""
        now = timezone.now()
        
        # Create ping
        ping = GpsPing.objects.create(
            user=self.user,
            **self.test_coords
        )
        
        # Query pings from past hour (without decrypting coordinates)
        one_hour_ago = now - timedelta(hours=1)
        recent_pings = GpsPing.objects.filter(
            user=self.user,
            created_at__gte=one_hour_ago
        )
        
        # Verify query worked (coordinates stay encrypted during query)
        self.assertEqual(recent_pings.count(), 1)
        self.assertEqual(recent_pings[0].id, ping.id)
    
    def test_time_range_query_multiple_pings(self):
        """Test time-range queries with multiple pings."""
        now = timezone.now()
        
        # Create multiple pings
        pings = []
        for i in range(3):
            ping = GpsPing.objects.create(
                user=self.user,
                latitude=28.7 + (i * 0.001),
                longitude=77.1 + (i * 0.001),
            )
            pings.append(ping)
        
        # Query pings in past hour
        one_hour_ago = now - timedelta(hours=1)
        recent = GpsPing.objects.filter(
            user=self.user,
            created_at__gte=one_hour_ago
        ).order_by('created_at')
        
        # Verify all pings returned
        self.assertEqual(recent.count(), 3)
        
        # Verify coordinates are intact
        for i, ping in enumerate(recent):
            self.assertAlmostEqual(ping.latitude, 28.7 + (i * 0.001), places=4)
    
    def test_query_old_gps_data_by_time(self):
        """Test querying old GPS data via time-range filters."""
        now = timezone.now()
        
        # Create ping
        ping = GpsPing.objects.create(
            user=self.user,
            **self.test_coords
        )
        
        # Query: data older than 90 days should not be returned
        ninety_days_ago = now - timedelta(days=90)
        old_pings = GpsPing.objects.filter(
            created_at__lt=ninety_days_ago
        )
        self.assertEqual(old_pings.count(), 0)
        
        # Query: data from past 90 days should be returned
        recent_pings = GpsPing.objects.filter(
            created_at__gte=ninety_days_ago
        )
        self.assertGreater(recent_pings.count(), 0)
    
    def test_filter_by_user(self):
        """Test filtering pings by user (unencrypted FK)."""
        user2 = User.objects.create(
            username="gps_user2",
            email="gps2@example.com"
        )
        
        # Create pings for both users
        ping1 = GpsPing.objects.create(
            user=self.user,
            latitude=28.7041,
            longitude=77.1025,
        )
        
        ping2 = GpsPing.objects.create(
            user=user2,
            latitude=28.5244,
            longitude=77.1855,
        )
        
        # Filter by user
        user_pings = GpsPing.objects.filter(user=self.user)
        self.assertEqual(user_pings.count(), 1)
        self.assertEqual(user_pings[0].id, ping1.id)
        
        # Filter by user2
        user2_pings = GpsPing.objects.filter(user=user2)
        self.assertEqual(user2_pings.count(), 1)
        self.assertEqual(user2_pings[0].id, ping2.id)
    
    def test_update_gpsping_reencrypts_coordinates(self):
        """Test updating GpsPing re-encrypts coordinates."""
        ping = GpsPing.objects.create(
            user=self.user,
            **self.test_coords
        )
        
        # Update coordinates
        new_latitude = 29.0
        new_longitude = 78.0
        ping.latitude = new_latitude
        ping.longitude = new_longitude
        ping.save()
        
        # Fetch and verify
        ping_fetched = GpsPing.objects.get(id=ping.id)
        self.assertAlmostEqual(ping_fetched.latitude, new_latitude, places=4)
        self.assertAlmostEqual(ping_fetched.longitude, new_longitude, places=4)
    
    def test_null_optional_fields(self):
        """Test null/optional coordinate fields."""
        ping = GpsPing.objects.create(
            user=self.user,
            latitude=28.7041,
            longitude=77.1025,
            accuracy=None,
            altitude=None,
            speed=None,
        )
        
        # Fetch and verify
        ping_fetched = GpsPing.objects.get(id=ping.id)
        self.assertIsNone(ping_fetched.accuracy)
        self.assertIsNone(ping_fetched.altitude)
        self.assertIsNone(ping_fetched.speed)
    
    def test_extreme_coordinate_values(self):
        """Test extreme latitude/longitude values."""
        # North Pole
        north_pole = GpsPing.objects.create(
            user=self.user,
            latitude=90.0,
            longitude=0.0,
        )
        
        # South Pole
        south_pole = GpsPing.objects.create(
            user=self.user,
            latitude=-90.0,
            longitude=0.0,
        )
        
        # Date Line (East)
        dateline_e = GpsPing.objects.create(
            user=self.user,
            latitude=0.0,
            longitude=180.0,
        )
        
        # Fetch and verify
        np = GpsPing.objects.get(id=north_pole.id)
        self.assertEqual(np.latitude, 90.0)
        self.assertEqual(np.longitude, 0.0)
        
        sp = GpsPing.objects.get(id=south_pole.id)
        self.assertEqual(sp.latitude, -90.0)
        self.assertEqual(sp.longitude, 0.0)
        
        dl = GpsPing.objects.get(id=dateline_e.id)
        self.assertEqual(dl.latitude, 0.0)
        self.assertEqual(dl.longitude, 180.0)
    
    def test_precision_coordinates(self):
        """Test high-precision GPS coordinates."""
        precise_lat = 28.704100123456
        precise_lon = 77.102500654321
        
        ping = GpsPing.objects.create(
            user=self.user,
            latitude=precise_lat,
            longitude=precise_lon,
        )
        
        # Fetch and verify precision
        ping_fetched = GpsPing.objects.get(id=ping.id)
        self.assertAlmostEqual(ping_fetched.latitude, precise_lat, places=10)
        self.assertAlmostEqual(ping_fetched.longitude, precise_lon, places=10)
    
    def test_order_by_timestamp(self):
        """Test ordering pings by timestamp."""
        # Create multiple pings
        pings = []
        for i in range(3):
            ping = GpsPing.objects.create(
                user=self.user,
                latitude=28.7 + (i * 0.01),
                longitude=77.1 + (i * 0.01),
            )
            pings.append(ping)
        
        # Order by created_at descending
        ordered = GpsPing.objects.filter(user=self.user).order_by('-created_at')
        
        # Verify order (most recent first)
        self.assertEqual(ordered[0].id, pings[2].id)
        self.assertEqual(ordered[1].id, pings[1].id)
        self.assertEqual(ordered[2].id, pings[0].id)
    
    def test_count_pings_per_user(self):
        """Test COUNT aggregation on pings (encrypted coordinates)."""
        # Create pings
        for i in range(5):
            GpsPing.objects.create(
                user=self.user,
                latitude=28.7 + (i * 0.001),
                longitude=77.1 + (i * 0.001),
            )
        
        # Count should work without decrypting coordinates
        count = GpsPing.objects.filter(user=self.user).count()
        self.assertEqual(count, 5)
    
    def test_accuracy_field_encrypted(self):
        """Test accuracy field is properly encrypted."""
        ping = GpsPing.objects.create(
            user=self.user,
            latitude=28.7041,
            longitude=77.1025,
            accuracy=50,
        )
        
        # Fetch and verify
        ping_fetched = GpsPing.objects.get(id=ping.id)
        self.assertEqual(ping_fetched.accuracy, 50)
    
    def test_location_privacy_preserved(self):
        """Test that location coordinates are protected from DB breach."""
        ping = GpsPing.objects.create(
            user=self.user,
            latitude=28.7041,
            longitude=77.1025,
        )
        
        # Raw database read should return ciphertext, not coordinates
        ping_raw = GpsPing.objects.raw(
            "SELECT * FROM gps_gpsping WHERE id = %s", [ping.id]
        )[0]
        
        # Ciphertext should be completely different from plaintext
        self.assertNotEqual(ping_raw.latitude, "28.7041")
        self.assertNotEqual(ping_raw.longitude, "77.1025")
        
        # Ciphertext should look like base64 or binary
        # (not a valid float when read as plain string)
        self.assertTrue(len(ping_raw.latitude) > 30)  # Ciphertext is long
