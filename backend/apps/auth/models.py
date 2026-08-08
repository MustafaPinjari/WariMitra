"""Authentication models for WariMitra"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import pre_save
from django.dispatch import receiver
from apps.core.models import BaseModel
from apps.core.fields import (
    EncryptedCharField,
    EncryptedEmailField,
    EncryptedPhoneField,
    create_searchable_hash_from_field
)
from apps.core.searchable_hash import SearchableHasher, get_hasher
import uuid


class User(AbstractUser, BaseModel):
    """
    Extended User model with encrypted PII fields.
    
    Phase 1.3: Implements field-level encryption for sensitive user data:
    - first_name: EncryptedCharField (transparent encryption)
    - last_name: EncryptedCharField (transparent encryption)
    - email: EncryptedEmailField with searchable hash (email_hash column)
    - phone_number: EncryptedPhoneField with searchable hash (phone_hash column)
    
    Encryption/decryption is transparent via Django ORM.
    Searchable hashes enable fast lookups without decryption.
    """
    id = models.BigAutoField(primary_key=True)
    
    # Encrypted PII fields (Phase 1.3)
    # Note: Django's AbstractUser already has 'first_name', 'last_name', 'email'
    # We override them with encrypted versions
    first_name = EncryptedCharField(max_length=100, blank=True)
    last_name = EncryptedCharField(max_length=100, blank=True)
    email = EncryptedEmailField(searchable=True, unique=False)  # Not unique due to encryption
    email_hash = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        db_index=True,
        unique=True,  # Unique constraint for searchable lookups
        editable=False
    )
    
    # Phone number encrypted with searchable hash
    phone_number = EncryptedPhoneField(
        max_length=20,
        blank=True,
        searchable=True
    )
    phone_hash = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        db_index=True,
        editable=False
    )
    
    user_type = models.CharField(
        max_length=20,
        choices=[
            ('pilgrim', 'Pilgrim'),
            ('medical_officer', 'Medical Officer'),
            ('police_officer', 'Police Officer'),
            ('admin', 'Administrator'),
        ],
        default='pilgrim'
    )
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"


@receiver(pre_save, sender=User)
def hash_user_email_field(sender, instance, **kwargs):
    """
    Signal handler to automatically compute email_hash on save.
    
    Called before User is saved to database. Computes PBKDF2 hash of email
    for searchable index. Hash enables fast lookups without decryption.
    """
    email = getattr(instance, 'email', None)
    if email:
        hasher = get_hasher()
        # Normalize email (lowercase, strip whitespace)
        normalized_email = SearchableHasher.normalize_input(email)
        email_hash = hasher.compute_hash(normalized_email)
        instance.email_hash = email_hash


@receiver(pre_save, sender=User)
def hash_user_phone_field(sender, instance, **kwargs):
    """
    Signal handler to automatically compute phone_hash on save.
    
    Called before User is saved to database. Computes PBKDF2 hash of phone
    for searchable index. Hash enables fast lookups without decryption.
    """
    phone = getattr(instance, 'phone_number', None)
    if phone:
        hasher = get_hasher()
        # Normalize phone (strip whitespace)
        normalized_phone = phone.strip()
        phone_hash = hasher.compute_hash(normalized_phone)
        instance.phone_hash = phone_hash


class TokenRevocation(BaseModel):
    """Audit log of token revocation events"""
    REVOCATION_REASONS = [
        ('logout', 'User logged out'),
        ('admin_revoke', 'Admin revoked all tokens'),
        ('password_reset', 'Password reset requested'),
        ('security_incident', 'Security incident detected'),
        ('device_lost', 'Device reported lost/stolen'),
    ]
    
    revocation_id = models.CharField(max_length=36, unique=True, db_index=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='token_revocations')
    revoked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='revoked_tokens')
    reason = models.CharField(max_length=50, choices=REVOCATION_REASONS)
    token_hash = models.CharField(max_length=64, db_index=True, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['revoked_by', 'created_at']),
        ]
    
    def __str__(self):
        return f"Revocation {self.revocation_id} for {self.user.username}"
