from django.db import models

class PublicToilet(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    gender_type = models.CharField(max_length=50, default='Unisex') # Male, Female, Unisex, Accessible
    cleanliness_score = models.IntegerField(default=85) # 0 to 100
    is_water_available = models.BooleanField(default=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return f"{self.name} ({self.cleanliness_score}%)"

class WasteReport(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending Dispatch'),
        ('CLEANING_DISPATCHED', 'Cleaning Crew Dispatched'),
        ('CLEANED', 'Resolved / Cleaned'),
    )

    location_name = models.CharField(max_length=200)
    waste_type = models.CharField(max_length=100) # Plastic, Organic, Overflowing Bin, Sewage
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='PENDING')
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.waste_type} at {self.location_name}"
