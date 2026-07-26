import uuid
from django.db import models
from django.conf import settings
from core.models import TimestampModel

class Hospital(TimestampModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    total_beds = models.IntegerField(default=0)
    available_beds = models.IntegerField(default=0)
    contact_number = models.CharField(max_length=15)

class MedicalCamp(TimestampModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    doctors_available = models.IntegerField(default=1)
    status = models.CharField(max_length=20, default='Active') # Active, Overcrowded, Closed

class Ambulance(TimestampModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle_number = models.CharField(max_length=20, unique=True)
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    status = models.CharField(max_length=20, default='Available') # Available, Dispatched, Maintenance

class MedicalCase(TimestampModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='medical_history')
    camp = models.ForeignKey(MedicalCamp, on_delete=models.SET_NULL, null=True, blank=True)
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='treated_cases')
    diagnosis = models.TextField()
    treatment = models.TextField()
    is_critical = models.BooleanField(default=False)
