from django.db import models
from django.conf import settings
from core.models import TimestampModel

class ServicePoint(TimestampModel):
    CATEGORY_CHOICES = (
        ('Water', 'Water Point / Tanker'),
        ('Medical', 'Medical Camp / First Aid'),
        ('Food', 'Food / Annadhana Stall'),
        ('Toilets', 'Public Toilet / Sanitation'),
        ('Shelter', 'Shelter / Rest Camp'),
        ('Police', 'Police Checkpoint / Security'),
        ('Help Desk', 'Help Desk / Information'),
        ('Parking', 'Vehicle Parking Area'),
        ('Other', 'Other Service'),
    )

    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Available', 'Available'),
        ('Busy', 'Busy'),
        ('Closed', 'Closed'),
    )

    name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Water')
    details = models.TextField(blank=True, default='')
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.CharField(max_length=255, blank=True, default='')
    contact_number = models.CharField(max_length=50, blank=True, default='')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Active')
    capacity_info = models.CharField(max_length=100, blank=True, default='')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='service_points')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} [{self.category}] ({self.status})"

