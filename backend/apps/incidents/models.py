"""Incidents app models."""

from django.db import models
from django.contrib.gis.db import models as gis_models
from apps.core.models import SoftDeleteModel


class Incident(SoftDeleteModel):
    """Incident model."""
    
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = gis_models.PointField(null=True, blank=True)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    
    def __str__(self):
        return self.title
