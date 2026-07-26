import uuid
from django.db import models
from core.models import TimestampModel

class QueuePrediction(TimestampModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    gate_id = models.CharField(max_length=50)
    predicted_wait_time = models.IntegerField(help_text="Predicted wait time in minutes")
    confidence_score = models.FloatField()
    valid_until = models.DateTimeField()
    
class CrowdForecast(TimestampModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sector_id = models.CharField(max_length=50)
    predicted_density = models.IntegerField(help_text="Predicted number of people")
    risk_level = models.CharField(max_length=20, default='Low') # Low, Medium, High, Critical
    valid_until = models.DateTimeField()

class RiskScore(TimestampModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    location_name = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    overall_risk_score = models.IntegerField(help_text="0 to 100")
    primary_risk_factor = models.CharField(max_length=100) # e.g. "Overcrowding", "Weather"
