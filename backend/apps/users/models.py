import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

class UserRole(models.TextChoices):
    PILGRIM = 'PILGRIM', 'Pilgrim'
    VOLUNTEER = 'VOLUNTEER', 'Volunteer'
    DINDI_LEADER = 'DINDI_LEADER', 'Dindi Leader'
    MEDICAL_STAFF = 'MEDICAL_STAFF', 'Medical Staff'
    POLICE_OFFICER = 'POLICE_OFFICER', 'Police Officer'
    NGO_COORDINATOR = 'NGO_COORDINATOR', 'NGO Coordinator'
    GOVERNMENT_ADMIN = 'GOVERNMENT_ADMIN', 'Government Admin'
    SUPER_ADMIN = 'SUPER_ADMIN', 'Super Admin'

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.PILGRIM
    )
    mobile = models.CharField(max_length=15, unique=True)
    is_verified = models.BooleanField(default=False)
    
    # We will use mobile for authentication instead of username.
    # AbstractUser requires username, but we'll override that in serializers/logic.
    
    def __str__(self):
        return f"{self.username} - {self.role}"
