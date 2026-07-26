import uuid
from django.db import models
from django.conf import settings
from core.models import TimestampModel

class PoliceStation(TimestampModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

class PatrolUnit(TimestampModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    officer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    station = models.ForeignKey(PoliceStation, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, default='Available') # Available, On_Patrol, Responding
    current_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

class RoadBlock(TimestampModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    reason = models.TextField()
    is_active = models.BooleanField(default=True)
