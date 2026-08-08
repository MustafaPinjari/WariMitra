"""GPS tracking models - Phase 1.3: Location coordinate encryption"""
from django.db import models
from apps.core.models import BaseModel
from apps.core.fields import (
    EncryptedFloatField,
    EncryptedIntegerField
)
from apps.auth.models import User


class GpsPing(BaseModel):
    """
    GPS location ping from user device - Phase 1.3: Encrypted coordinates
    
    Encrypted fields (coordinates):
    - latitude: GPS latitude (encrypted with EncryptedFloatField)
    - longitude: GPS longitude (encrypted with EncryptedFloatField)
    - accuracy: GPS accuracy in meters (encrypted)
    - altitude: Elevation above sea level (encrypted)
    
    Unencrypted fields (required for time-based queries):
    - timestamp (created_at): NOT encrypted - required for time-range queries
    
    Security properties:
    - Location coordinates encrypted to protect user privacy
    - Location history cannot be reconstructed from DB breach
    - Time-range queries still work without decryption
    - User movement patterns protected
    
    Phase 2.2: Move to TimescaleDB for time-series storage
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gps_pings')
    latitude = EncryptedFloatField()
    longitude = EncryptedFloatField()
    accuracy = EncryptedIntegerField(null=True, blank=True)
    altitude = EncryptedFloatField(null=True, blank=True)
    speed = EncryptedFloatField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"GPS ping from {self.user.username} at {self.created_at}"


class LiveDensity(BaseModel):
    """Real-time crowd density data - Phase 2.2: Move to Redis"""
    latitude = models.FloatField()
    longitude = models.FloatField()
    density_level = models.IntegerField()  # 0-100 scale
    radius = models.IntegerField(default=100)  # meters
    
    class Meta:
        ordering = ['-created_at']
