import uuid
from django.db import models
from django.conf import settings
from core.models import TimestampModel

class TempleQueue(TimestampModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    queue_type = models.CharField(max_length=50) # General, Senior, VIP
    gate_id = models.CharField(max_length=50)
    capacity = models.IntegerField(default=1000)
    current_count = models.IntegerField(default=0)
    average_wait_time = models.IntegerField(default=0) # in minutes
    status = models.CharField(max_length=20, default='Open') # Open, Closed, Full

class DarshanSlot(TimestampModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    queue = models.ForeignKey(TempleQueue, on_delete=models.CASCADE, related_name='slots')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    capacity = models.IntegerField(default=100)
    occupied = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default='Available') # Available, Full

class QueueMovement(TimestampModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    queue = models.ForeignKey(TempleQueue, on_delete=models.CASCADE)
    entries = models.IntegerField(default=0)
    exits = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
