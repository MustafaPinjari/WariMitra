"""
Redis Live Density Manager
Phase 2.2 Implementation: Database Bottleneck (Transaction Locks) Mitigation

Manages live density tracking using Redis GEO commands for ultra-fast, 
non-locking geospatial queries instead of PostgreSQL.
"""
import redis
from django.conf import settings
from django.utils import timezone

class LiveDensityManager:
    """
    Redis-backed density manager for live crowd monitoring.
    
    Features:
    - O(log(N)) spatial queries via Redis GEOADD/GEORADIUS
    - No PostgreSQL transaction locks
    - Automatic TTL (can be implemented via ZSET pruning)
    """
    
    KEY = 'gps:live_density'
    
    def __init__(self):
        try:
            self.redis_client = redis.StrictRedis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
            )
            self.redis_client.ping()
            self.is_connected = True
        except Exception as e:
            print(f"⚠️ Redis connection warning: {e}")
            self.is_connected = False
            
    def update_density(self, user_id, latitude, longitude):
        """Update a user's current location in the density map."""
        if not self.is_connected:
            return False
            
        # Store user_id at the given coordinates
        self.redis_client.geoadd(self.KEY, (longitude, latitude, str(user_id)))
        return True
        
    def get_density_in_radius(self, latitude, longitude, radius_meters=100):
        """Get the number of unique users within a given radius."""
        if not self.is_connected:
            return 0
            
        results = self.redis_client.georadius(
            self.KEY, 
            longitude, 
            latitude, 
            radius_meters, 
            unit='m'
        )
        return len(results)
        
    def get_density_level(self, latitude, longitude, radius_meters=100):
        """Returns a density level 0-100 based on count."""
        count = self.get_density_in_radius(latitude, longitude, radius_meters)
        # Normalize: say 500 people in 100m radius is max density (100)
        level = min(100, int((count / 500.0) * 100))
        return level
