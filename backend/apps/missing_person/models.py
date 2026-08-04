import uuid
from django.db import models
from django.conf import settings
from core.models import TimestampModel


class MissingPersonCategory(models.TextChoices):
    CHILD = 'Child', 'Child'
    ELDERLY = 'Elderly', 'Elderly'
    ADULT = 'Adult', 'Adult'
    DISABLED = 'Disabled', 'Disabled'


class MissingPersonStatus(models.TextChoices):
    SEARCHING = 'Searching', 'Searching'
    FOUND = 'Found', 'Found'
    CLOSED = 'Closed', 'Closed'


class MissingPersonReport(TimestampModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='missing_person_reports'
    )
    name = models.CharField(max_length=255)
    age = models.IntegerField(null=True, blank=True)
    category = models.CharField(max_length=20, choices=MissingPersonCategory.choices, default=MissingPersonCategory.ADULT)
    description = models.TextField(blank=True)
    photo = models.ImageField(upload_to='missing_persons/', blank=True, null=True)
    photo_url = models.CharField(max_length=500, blank=True, null=True)
    last_seen_location = models.CharField(max_length=255, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    status = models.CharField(max_length=20, choices=MissingPersonStatus.choices, default=MissingPersonStatus.SEARCHING)
    contact_mobile = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"Missing: {self.name} ({self.category}) - {self.status}"
