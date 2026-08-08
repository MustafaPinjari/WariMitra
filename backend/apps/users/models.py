"""Users app models."""

from apps.core.models import SoftDeleteModel
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class UserProfile(SoftDeleteModel):
    """Extended user profile information."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    
    def __str__(self):
        return f"Profile of {self.user.username}"
