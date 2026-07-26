import uuid
from django.db import models
from django.conf import settings
from core.models import TimestampModel

class EmergencyType(models.TextChoices):
    MEDICAL = 'Medical', 'Medical Emergency'
    ACCIDENT = 'Accident', 'Accident'
    LOST_PERSON = 'Lost_Person', 'Lost Person'
    WOMEN_SAFETY = 'Women_Safety', 'Women Safety'
    CHILD_SAFETY = 'Child_Safety', 'Child Safety'
    FIRE = 'Fire', 'Fire'
    CROWD_INCIDENT = 'Crowd_Incident', 'Crowd Incident'
    SECURITY_THREAT = 'Security_Threat', 'Security Threat'
    OTHER = 'Other', 'Other'

class IncidentPriority(models.TextChoices):
    CRITICAL = 'Critical', 'Critical'
    HIGH = 'High', 'High'
    MEDIUM = 'Medium', 'Medium'
    LOW = 'Low', 'Low'

class IncidentStatus(models.TextChoices):
    NEW = 'New', 'New'
    RESPONDER_ASSIGNED = 'Responder_Assigned', 'Responder Assigned'
    IN_PROGRESS = 'In_Progress', 'In Progress'
    RESOLVED = 'Resolved', 'Resolved'
    CLOSED = 'Closed', 'Closed'

class EmergencyIncident(TimestampModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sos_requests')
    emergency_type = models.CharField(max_length=50, choices=EmergencyType.choices)
    priority = models.CharField(max_length=20, choices=IncidentPriority.choices, default=IncidentPriority.HIGH)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=30, choices=IncidentStatus.choices, default=IncidentStatus.NEW)
    photo_url = models.URLField(max_length=500, blank=True, null=True)
    
    def __str__(self):
        return f"{self.emergency_type} - {self.status}"

class EmergencyResponder(TimestampModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    incident = models.ForeignKey(EmergencyIncident, on_delete=models.CASCADE, related_name='responders')
    responder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='emergency_responses')
    responder_type = models.CharField(max_length=50) # e.g. Volunteer, Police, Ambulance
    accepted_at = models.DateTimeField(auto_now_add=True)
    eta_minutes = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.responder.username} -> {self.incident.id}"

class EmergencyLog(TimestampModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    incident = models.ForeignKey(EmergencyIncident, on_delete=models.CASCADE, related_name='logs')
    action = models.CharField(max_length=255)
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return f"{self.incident.id} - {self.action}"
