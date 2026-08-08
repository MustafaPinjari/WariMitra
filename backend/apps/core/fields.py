"""
Custom Django Model Fields for Encrypted Storage.

Provides transparent encryption/decryption at the field level:
- EncryptedCharField: CharField with encryption
- EncryptedTextField: TextField with encryption
- EncryptedEmailField: EmailField with searchable hash column
- EncryptedPhoneField: CharField with searchable hash column
- EncryptedIntegerField: IntegerField with encryption
- EncryptedFloatField: FloatField with encryption

Usage:
    from apps.core.fields import EncryptedCharField, EncryptedEmailField
    
    class User(models.Model):
        first_name = EncryptedCharField(max_length=100)
        email = EncryptedEmailField(searchable=True)
        phone = EncryptedPhoneField(searchable=True)
"""

from django.db import models
from django.core.exceptions import ValidationError
from apps.core.encryption import EncryptionEngine, EncryptionIntegrityError, EncryptionFormatError
from apps.core.searchable_hash import SearchableHasher, get_hasher
from apps.core.key_manager import get_key_manager
import logging

logger = logging.getLogger(__name__)


class EncryptedFieldMixin:
    """
    Mixin for encrypted fields that adds encryption/decryption behavior.
    """
    
    def get_prep_value(self, value):
        """
        Prepare value for database storage by encrypting it.
        
        Called before saving to database. Encrypts plaintext to ciphertext.
        """
        if value is None:
            return None
        
        try:
            # Get current encryption key
            manager = get_key_manager()
            key = manager.get_current_key()
            engine = EncryptionEngine(key)
            
            # Convert value to string and encrypt
            plaintext = str(value)
            ciphertext = engine.encrypt(plaintext)
            
            return ciphertext
        
        except Exception as e:
            logger.error(f"Encryption failed for field {self.name}: {str(e)}")
            raise
    
    def from_db_value(self, value, expression, connection):
        """
        Decrypt value loaded from database.
        
        Called after loading from database. Attempts to decrypt ciphertext.
        Falls back to plaintext if decryption fails (backwards compatibility).
        
        Note: Audit logging for decryption is handled by the model's from_db_value
        or a pre/post-load signal handler to have access to the model instance.
        """
        if value is None:
            return None
        
        try:
            # Try to decrypt
            manager = get_key_manager()
            key = manager.get_current_key()
            engine = EncryptionEngine(key)
            
            plaintext = engine.decrypt(value)
            return plaintext
        
        except EncryptionIntegrityError:
            # Ciphertext corrupted or tampered
            logger.warning(f"Failed to decrypt field {self.name}: integrity check failed")
            raise
        
        except EncryptionFormatError:
            # Not encrypted data - try to use as plaintext (backwards compatibility)
            logger.debug(f"Field {self.name} appears to be plaintext (not encrypted)")
            return value
        
        except Exception as e:
            logger.error(f"Decryption failed for field {self.name}: {str(e)}")
            raise
    
    def deconstruct(self):
        """
        Return field deconstruction for migrations.
        """
        name, path, args, kwargs = super().deconstruct()
        return name, path, args, kwargs


class EncryptedCharField(EncryptedFieldMixin, models.CharField):
    """
    CharField with transparent AES-256-GCM encryption.
    
    Usage:
        first_name = EncryptedCharField(max_length=100)
    """
    pass


class EncryptedTextField(EncryptedFieldMixin, models.TextField):
    """
    TextField with transparent AES-256-GCM encryption.
    
    Usage:
        bio = EncryptedTextField()
    """
    pass


class EncryptedEmailField(EncryptedFieldMixin, models.EmailField):
    """
    EmailField with encryption and optional searchable hash.
    
    If searchable=True, automatically creates email_hash column for lookups.
    
    Usage:
        email = EncryptedEmailField(searchable=True)
        # Creates email_hash column automatically
    """
    
    def __init__(self, *args, searchable=False, **kwargs):
        self.searchable = searchable
        super().__init__(*args, **kwargs)
    
    def contribute_to_class(self, cls, name, **kwargs):
        """
        Add hash field if searchable=True.
        """
        super().contribute_to_class(cls, name, **kwargs)
        
        if self.searchable:
            # Create hash field
            hash_field = models.CharField(
                max_length=64,
                null=True,
                blank=True,
                db_index=True,
                editable=False
            )
            hash_field.creation_counter = self.creation_counter + 0.1
            hash_field.contribute_to_class(cls, f'{name}_hash')
    
    def get_prep_value(self, value):
        """
        Override to handle hash generation.
        """
        return super().get_prep_value(value)


class EncryptedPhoneField(EncryptedFieldMixin, models.CharField):
    """
    Phone number field with encryption and optional searchable hash.
    
    If searchable=True, automatically creates phone_hash column for lookups.
    
    Usage:
        phone = EncryptedPhoneField(max_length=20, searchable=True)
        # Creates phone_hash column automatically
    """
    
    def __init__(self, *args, searchable=False, **kwargs):
        if 'max_length' not in kwargs:
            kwargs['max_length'] = 20
        self.searchable = searchable
        super().__init__(*args, **kwargs)
    
    def contribute_to_class(self, cls, name, **kwargs):
        """
        Add hash field if searchable=True.
        """
        super().contribute_to_class(cls, name, **kwargs)
        
        if self.searchable:
            # Create hash field
            hash_field = models.CharField(
                max_length=64,
                null=True,
                blank=True,
                db_index=True,
                editable=False
            )
            hash_field.creation_counter = self.creation_counter + 0.1
            hash_field.contribute_to_class(cls, f'{name}_hash')


class EncryptedIntegerField(EncryptedFieldMixin, models.IntegerField):
    """
    IntegerField with transparent encryption.
    
    Note: Encrypted integers cannot be sorted or compared in database.
    For range queries, keep the field unencrypted and store separately.
    
    Usage:
        age = EncryptedIntegerField()
    """
    
    def get_prep_value(self, value):
        """
        Override to encrypt integer values.
        """
        if value is None:
            return None
        
        try:
            manager = get_key_manager()
            key = manager.get_current_key()
            engine = EncryptionEngine(key)
            
            # Convert integer to string, encrypt
            plaintext = str(value)
            ciphertext = engine.encrypt(plaintext)
            
            return ciphertext
        except Exception as e:
            logger.error(f"Encryption failed for IntegerField {self.name}: {str(e)}")
            raise
    
    def from_db_value(self, value, expression, connection):
        """
        Decrypt and convert back to integer.
        """
        if value is None:
            return None
        
        try:
            manager = get_key_manager()
            key = manager.get_current_key()
            engine = EncryptionEngine(key)
            
            # Decrypt and convert to integer
            plaintext = engine.decrypt(value)
            return int(plaintext)
        
        except (EncryptionIntegrityError, EncryptionFormatError):
            # Try as plaintext
            try:
                return int(value)
            except (ValueError, TypeError):
                logger.error(f"Failed to parse IntegerField {self.name}")
                raise
        
        except Exception as e:
            logger.error(f"Decryption failed for IntegerField {self.name}: {str(e)}")
            raise


class EncryptedFloatField(EncryptedFieldMixin, models.FloatField):
    """
    FloatField with transparent encryption.
    
    Note: Encrypted floats cannot be used for comparisons or calculations.
    
    Usage:
        latitude = EncryptedFloatField()
        longitude = EncryptedFloatField()
    """
    
    def get_prep_value(self, value):
        """
        Override to encrypt float values.
        """
        if value is None:
            return None
        
        try:
            manager = get_key_manager()
            key = manager.get_current_key()
            engine = EncryptionEngine(key)
            
            # Convert float to string, encrypt
            plaintext = str(value)
            ciphertext = engine.encrypt(plaintext)
            
            return ciphertext
        except Exception as e:
            logger.error(f"Encryption failed for FloatField {self.name}: {str(e)}")
            raise
    
    def from_db_value(self, value, expression, connection):
        """
        Decrypt and convert back to float.
        """
        if value is None:
            return None
        
        try:
            manager = get_key_manager()
            key = manager.get_current_key()
            engine = EncryptionEngine(key)
            
            # Decrypt and convert to float
            plaintext = engine.decrypt(value)
            return float(plaintext)
        
        except (EncryptionIntegrityError, EncryptionFormatError):
            # Try as plaintext
            try:
                return float(value)
            except (ValueError, TypeError):
                logger.error(f"Failed to parse FloatField {self.name}")
                raise
        
        except Exception as e:
            logger.error(f"Decryption failed for FloatField {self.name}: {str(e)}")
            raise


def create_searchable_hash_from_field(sender, instance, field_name, **kwargs):
    """
    Signal receiver to automatically create searchable hash when field is saved.
    
    Usage in models.py:
        from django.db.models.signals import pre_save
        from django.dispatch import receiver
        
        @receiver(pre_save, sender=User)
        def hash_email_field(sender, instance, **kwargs):
            create_searchable_hash_from_field(
                sender, instance, 'email', **kwargs
            )
    """
    value = getattr(instance, field_name, None)
    hash_field_name = f'{field_name}_hash'
    
    if value and hasattr(instance, hash_field_name):
        hasher = get_hasher()
        # Normalize for emails
        if field_name == 'email':
            value = SearchableHasher.normalize_input(value)
        hash_value = hasher.compute_hash(value)
        setattr(instance, hash_field_name, hash_value)
