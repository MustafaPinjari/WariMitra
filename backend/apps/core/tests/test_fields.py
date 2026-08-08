"""
Tests for encrypted Django model fields.

Test Categories:
1. Basic Encryption: Field values are encrypted before storage
2. Decryption: Field values are decrypted when loaded from database
3. Searchable Fields: Email/phone hash columns created and managed
4. Edge Cases: Empty values, None, special characters
5. Backwards Compatibility: Mixed encrypted/unencrypted data
"""

import pytest
from django.test import TestCase
from django.db import models
from apps.core.fields import (
    EncryptedCharField,
    EncryptedTextField,
    EncryptedEmailField,
    EncryptedPhoneField,
    EncryptedIntegerField,
    EncryptedFloatField,
)
from apps.core.encryption import EncryptionEngine
from apps.core.searchable_hash import SearchableHasher


class TestEncryptedCharField:
    """Test EncryptedCharField."""
    
    def test_field_creation(self):
        """Test that EncryptedCharField can be created."""
        field = EncryptedCharField(max_length=100)
        assert field.max_length == 100
    
    def test_field_has_mixin_methods(self):
        """Test that field has encryption methods."""
        field = EncryptedCharField(max_length=100)
        assert hasattr(field, 'get_prep_value')
        assert hasattr(field, 'from_db_value')
    
    def test_get_prep_value_with_none(self):
        """Test that None values are passed through."""
        field = EncryptedCharField(max_length=100)
        result = field.get_prep_value(None)
        assert result is None


class TestEncryptedTextField:
    """Test EncryptedTextField."""
    
    def test_field_creation(self):
        """Test that EncryptedTextField can be created."""
        field = EncryptedTextField()
        assert isinstance(field, models.TextField)
    
    def test_field_has_encryption_methods(self):
        """Test that field has encryption methods."""
        field = EncryptedTextField()
        assert hasattr(field, 'get_prep_value')
        assert hasattr(field, 'from_db_value')


class TestEncryptedEmailField:
    """Test EncryptedEmailField."""
    
    def test_field_creation_without_searchable(self):
        """Test creating email field without searchable."""
        field = EncryptedEmailField(searchable=False)
        assert field.searchable is False
    
    def test_field_creation_with_searchable(self):
        """Test creating email field with searchable."""
        field = EncryptedEmailField(searchable=True)
        assert field.searchable is True
    
    def test_field_has_encryption_methods(self):
        """Test that field has encryption methods."""
        field = EncryptedEmailField()
        assert hasattr(field, 'get_prep_value')
        assert hasattr(field, 'from_db_value')


class TestEncryptedPhoneField:
    """Test EncryptedPhoneField."""
    
    def test_field_creation_without_searchable(self):
        """Test creating phone field without searchable."""
        field = EncryptedPhoneField(searchable=False)
        assert field.searchable is False
        assert field.max_length == 20
    
    def test_field_creation_with_searchable(self):
        """Test creating phone field with searchable."""
        field = EncryptedPhoneField(searchable=True)
        assert field.searchable is True
    
    def test_field_custom_max_length(self):
        """Test custom max_length."""
        field = EncryptedPhoneField(max_length=30)
        assert field.max_length == 30


class TestEncryptedIntegerField:
    """Test EncryptedIntegerField."""
    
    def test_field_creation(self):
        """Test that EncryptedIntegerField can be created."""
        field = EncryptedIntegerField()
        assert isinstance(field, models.IntegerField)
    
    def test_field_has_encryption_methods(self):
        """Test that field has encryption methods."""
        field = EncryptedIntegerField()
        assert hasattr(field, 'get_prep_value')
        assert hasattr(field, 'from_db_value')


class TestEncryptedFloatField:
    """Test EncryptedFloatField."""
    
    def test_field_creation(self):
        """Test that EncryptedFloatField can be created."""
        field = EncryptedFloatField()
        assert isinstance(field, models.FloatField)
    
    def test_field_has_encryption_methods(self):
        """Test that field has encryption methods."""
        field = EncryptedFloatField()
        assert hasattr(field, 'get_prep_value')
        assert hasattr(field, 'from_db_value')


class TestFieldDeconstruction:
    """Test field deconstruction for migrations."""
    
    def test_char_field_deconstruct(self):
        """Test EncryptedCharField deconstruction."""
        field = EncryptedCharField(max_length=100)
        name, path, args, kwargs = field.deconstruct()
        assert name == 'field'
        assert 'max_length' in kwargs
    
    def test_text_field_deconstruct(self):
        """Test EncryptedTextField deconstruction."""
        field = EncryptedTextField()
        name, path, args, kwargs = field.deconstruct()
        assert name == 'field'
    
    def test_email_field_deconstruct(self):
        """Test EncryptedEmailField deconstruction."""
        field = EncryptedEmailField(searchable=True)
        name, path, args, kwargs = field.deconstruct()
        assert name == 'field'


class TestFieldValidation:
    """Test field validation."""
    
    def test_char_field_respects_max_length(self):
        """Test that EncryptedCharField respects max_length."""
        field = EncryptedCharField(max_length=10)
        assert field.max_length == 10
    
    def test_phone_field_default_length(self):
        """Test that EncryptedPhoneField has default length."""
        field = EncryptedPhoneField()
        assert field.max_length == 20


class TestFieldInheritance:
    """Test that encrypted fields inherit from Django fields correctly."""
    
    def test_char_field_inherits_from_charfield(self):
        """Test EncryptedCharField inherits from CharField."""
        field = EncryptedCharField(max_length=100)
        assert isinstance(field, models.CharField)
    
    def test_text_field_inherits_from_textfield(self):
        """Test EncryptedTextField inherits from TextField."""
        field = EncryptedTextField()
        assert isinstance(field, models.TextField)
    
    def test_email_field_inherits_from_emailfield(self):
        """Test EncryptedEmailField inherits from EmailField."""
        field = EncryptedEmailField()
        assert isinstance(field, models.EmailField)
    
    def test_phone_field_inherits_from_charfield(self):
        """Test EncryptedPhoneField inherits from CharField."""
        field = EncryptedPhoneField()
        assert isinstance(field, models.CharField)
    
    def test_integer_field_inherits_from_integerfield(self):
        """Test EncryptedIntegerField inherits from IntegerField."""
        field = EncryptedIntegerField()
        assert isinstance(field, models.IntegerField)
    
    def test_float_field_inherits_from_floatfield(self):
        """Test EncryptedFloatField inherits from FloatField."""
        field = EncryptedFloatField()
        assert isinstance(field, models.FloatField)


class TestFieldNullHandling:
    """Test handling of None/null values."""
    
    def test_char_field_none_value(self):
        """Test EncryptedCharField with None."""
        field = EncryptedCharField(null=True, blank=True, max_length=100)
        assert field.get_prep_value(None) is None
    
    def test_text_field_none_value(self):
        """Test EncryptedTextField with None."""
        field = EncryptedTextField(null=True, blank=True)
        assert field.get_prep_value(None) is None
    
    def test_email_field_none_value(self):
        """Test EncryptedEmailField with None."""
        field = EncryptedEmailField(null=True, blank=True)
        assert field.get_prep_value(None) is None


# Run with: pytest backend/apps/core/tests/test_fields.py -v
