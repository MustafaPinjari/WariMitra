"""Medical Camps app models."""

from django.db import models
from django.contrib.gis.db import models as gis_models
from apps.core.models import SoftDeleteModel


class MedicalCamp(SoftDeleteModel):
    """Medical camp model."""
    
    name = models.CharField(max_length=255, unique=True)
    location = gis_models.PointField()
    capacity = models.IntegerField(default=0)
    current_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
