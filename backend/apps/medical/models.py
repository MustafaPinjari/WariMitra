"""Medical models"""
from django.db import models
from apps.core.models import BaseModel
from apps.core.fields import (
    EncryptedCharField,
    EncryptedTextField,
    EncryptedIntegerField
)
from apps.auth.models import User


class MedicalCamp(BaseModel):
    """Medical aid camp location"""
    name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    capacity = models.IntegerField()
    current_patients = models.IntegerField(default=0)
    staff = models.ManyToManyField(User, related_name='medical_camps')
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Patient(BaseModel):
    """
    Patient record - Phase 1.3: Field-level encryption of medical data
    
    Encrypted fields:
    - first_name: Patient's given name (encrypted)
    - last_name: Patient's family name (encrypted)
    - age: Patient's age (encrypted as integer)
    - condition: Medical condition description (encrypted)
    
    Unencrypted fields:
    - medical_camp: Foreign key reference (needed for queries)
    - created_at: Timestamp (needed for time-based queries)
    
    Security properties:
    - All PII encrypted with AES-256-GCM
    - Supports aggregate queries (COUNT) on encrypted data
    - Backwards compatible with unencrypted records
    - Audit logging tracks medical data access
    """
    medical_camp = models.ForeignKey(MedicalCamp, on_delete=models.PROTECT, related_name='patients')
    first_name = EncryptedCharField(max_length=255)
    last_name = EncryptedCharField(max_length=255)
    age = EncryptedIntegerField(null=True, blank=True)
    condition = EncryptedTextField()
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['medical_camp', 'created_at']),
        ]
    
    def __str__(self):
        return f"Patient at {self.medical_camp.name} (ID: {self.id})"
