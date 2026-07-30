import uuid
from django.db import models
from django.conf import settings
from core.models import TimestampModel

class Dindi(TimestampModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=100, unique=True)
    leader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='led_dindis')

    def __str__(self):
        return self.name

class PilgrimProfile(TimestampModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True, related_name='pilgrim_profile')
    dindi = models.ForeignKey(Dindi, on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], blank=True)
    blood_group = models.CharField(max_length=5, blank=True)
    medical_conditions = models.TextField(blank=True, help_text="List any chronic diseases or allergies")
    qr_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    
    def __str__(self):
        return f"Profile for {self.user.username}"

class FamilyGroup(TimestampModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_family_groups')
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='family_groups')
    
    def __str__(self):
        return self.name

class EmergencyContact(TimestampModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pilgrim = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='emergency_contacts')
    name = models.CharField(max_length=255)
    relationship = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    
    def __str__(self):
        return f"{self.name} ({self.relationship}) - {self.mobile}"


class LiveLocation(models.Model):
    """Stores the latest known GPS position of a user. Updated on app open/SOS."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='live_location'
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    updated_at = models.DateTimeField(auto_now=True)
    battery_level = models.IntegerField(null=True, blank=True)  # 0-100

    def __str__(self):
        return f"{self.user.username} @ ({self.latitude}, {self.longitude})"
