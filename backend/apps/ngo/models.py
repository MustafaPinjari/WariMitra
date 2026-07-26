import uuid
from django.db import models
from django.conf import settings
from core.models import TimestampModel

class ResourceType(models.TextChoices):
    WATER = 'Water', 'Water'
    FOOD = 'Food', 'Food'
    MEDICINE = 'Medicine', 'Medicine'
    BLANKET = 'Blanket', 'Blanket'
    OTHER = 'Other', 'Other'

class Resource(TimestampModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ngo_coordinator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    resource_type = models.CharField(max_length=50, choices=ResourceType.choices)
    unit = models.CharField(max_length=50) # e.g., Litres, Packets, Boxes

class Inventory(TimestampModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='inventory')
    quantity = models.IntegerField(default=0)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    status = models.CharField(max_length=20, default='Available')

class Distribution(TimestampModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    quantity_distributed = models.IntegerField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    distributed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
class Donation(TimestampModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    donor_name = models.CharField(max_length=255)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    quantity = models.IntegerField()
