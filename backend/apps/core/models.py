"""Core models for WariMitra"""
from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords


class SoftDeleteModel(models.Model):
    """Abstract base model with soft delete support"""
    is_active = models.BooleanField(default=True, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)
    
    class Meta:
        abstract = True
    
    def delete(self, *args, **kwargs):
        """Soft delete: mark as inactive instead of actually deleting"""
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save()
    
    def hard_delete(self, *args, **kwargs):
        """Actually delete from database (use with caution)"""
        super().delete(*args, **kwargs)


class TimeStampedModel(models.Model):
    """Abstract base model with created and updated timestamps"""
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    
    class Meta:
        abstract = True


class BaseModel(SoftDeleteModel, TimeStampedModel):
    """Base model combining soft delete and timestamps"""
    history = HistoricalRecords(inherit=True)
    
    class Meta:
        abstract = True
