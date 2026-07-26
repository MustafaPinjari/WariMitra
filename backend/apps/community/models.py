import uuid
from django.db import models
from django.conf import settings
from core.models import TimestampModel

class ReportCategory(models.TextChoices):
    WATER = 'Water', 'Water'
    FOOD = 'Food', 'Food'
    MEDICAL = 'Medical', 'Medical'
    TRAFFIC = 'Traffic', 'Traffic'
    ROAD_BLOCK = 'Road_Block', 'Road Block'
    OTHER = 'Other', 'Other'

class ReportStatus(models.TextChoices):
    NEW = 'New', 'New'
    UNDER_REVIEW = 'Under_Review', 'Under Review'
    VERIFIED = 'Verified', 'Verified'
    ASSIGNED = 'Assigned', 'Assigned'
    IN_PROGRESS = 'In_Progress', 'In Progress'
    RESOLVED = 'Resolved', 'Resolved'
    CLOSED = 'Closed', 'Closed'

class CommunityReport(TimestampModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='submitted_reports')
    category = models.CharField(max_length=50, choices=ReportCategory.choices)
    description = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    priority = models.CharField(max_length=20, default='Medium')
    confidence_score = models.IntegerField(default=50) # 0-100
    verification_status = models.CharField(max_length=50, default='Pending')
    status = models.CharField(max_length=50, choices=ReportStatus.choices, default=ReportStatus.NEW)
    
    def __str__(self):
        return f"{self.category} Report by {self.reporter}"

class ReportVerification(TimestampModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(CommunityReport, on_delete=models.CASCADE, related_name='verifications')
    verifier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='verified_reports')
    verifier_role = models.CharField(max_length=50)
    is_valid = models.BooleanField()
    remarks = models.TextField(blank=True, null=True)

class ReporterTrust(TimestampModel):
    reporter = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    trust_score = models.IntegerField(default=50)
    total_reports = models.IntegerField(default=0)
    verified_reports = models.IntegerField(default=0)
    false_reports = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Trust Score for {self.reporter}: {self.trust_score}"
