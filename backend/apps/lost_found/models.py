from django.db import models

class LostFoundItem(models.Model):
    STATUS_CHOICES = (
        ('REPORTED', 'Reported Lost'),
        ('FOUND', 'Found in Storage'),
        ('CLAIM_PENDING', 'Claim Pending Verification'),
        ('RETURNED', 'Returned to Owner'),
    )

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=100) # Bag, Phone, ID Card, Jewels, Clothing
    description = models.TextField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='REPORTED')
    location = models.CharField(max_length=200)
    contact_phone = models.CharField(max_length=20)
    image = models.ImageField(upload_to='lost_found/', blank=True, null=True)
    image_url = models.CharField(max_length=500, blank=True, null=True)
    qr_claim_code = models.CharField(max_length=100, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.status})"
